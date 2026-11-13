"""Local web server: the Phiversity frontend wired to the render pipeline.

Serves the static frontend from <root>/Frontend and exposes the JSON API
the app pages use:

  GET  /api/config                 themes, voices, bundled topics, whether
                                   an LLM key is configured
  POST /api/generate               start a render job
                                   {question? | topic?, quality?, voice?,
                                    tts?, theme?, captions?, transitions?,
                                    max_segments?}
  GET  /api/jobs                   job list
  GET  /api/jobs/{id}              status, stage, progress, live log tail
  GET  /api/lectures               generated lectures (from manifests)
  GET  /api/lectures/{slug}/video  the mp4 (with HTTP Range support)

Jobs run sequentially on a worker thread; log output from the pipeline is
streamed into the job record so the progress page can show it live. No
external web framework is required.
"""

from __future__ import annotations

import json
import mimetypes
import os
import queue
import re
import threading
import time
import uuid
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .config import PipelineConfig, TTSConfig, RenderConfig, LLMConfig, \
    load_env_file
from .db import Database, is_sqlite_file
from .llm import LLMClient, LLMError
from .media import cloudinary_configured, destroy, upload_video
from .pipeline import Pipeline, Segment, run_pipeline
from .store import open_store
from .templates import BUNDLED_LECTURES, normalize_topic, bundled_topics

MAX_LOG_LINES = 400
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

# stage shown in the pipeline log "[N/5] ..." -> label + coarse progress
STAGES = {1: ("plan", 8), 2: ("speak", 18), 3: ("code", 32),
          4: ("render", 58), 5: ("compose", 90)}


@dataclass
class Job:
    id: str
    created: float = field(default_factory=time.time)
    status: str = "queued"        # queued | running | done | error
    stage: str = "-"
    progress: int = 0
    title: str = ""
    question: str = ""
    topic: str = ""
    video: str = ""
    error: str = ""
    logs: list = field(default_factory=list)
    user_id: str = ""             # Supabase auth user ("" when anonymous)
    payload: dict = field(default_factory=dict)   # request options, kept
                                                  # so a standalone worker
                                                  # can restart the job
    persist: object = None        # set by the server: flush to the store

    def log(self, line: str) -> None:
        self.logs.append(line)
        if len(self.logs) > MAX_LOG_LINES:
            del self.logs[:len(self.logs) - MAX_LOG_LINES]
        text = line.strip()
        changed = False
        match = re.match(r"\[(\d)/5\]", text)
        if match:
            self.stage, self.progress = STAGES[int(match.group(1))]
            changed = True
        if text.startswith("done"):
            self.progress = 100
            changed = True
        if changed and self.persist is not None:
            self.persist()

    def to_record(self) -> dict:
        return {"id": self.id, "created": self.created,
                "status": self.status, "stage": self.stage,
                "progress": self.progress, "title": self.title,
                "question": self.question, "topic": self.topic,
                "video": self.video, "error": self.error,
                "logs": self.logs, "user_id": self.user_id,
                "payload": self.payload}

    @classmethod
    def from_record(cls, record: dict) -> "Job":
        return cls(id=record["id"], created=record["created"],
                   status=record["status"], stage=record["stage"],
                   progress=record["progress"], title=record["title"],
                   question=record["question"], topic=record["topic"],
                   video=record["video"], error=record["error"],
                   logs=list(record.get("logs", [])),
                   user_id=record.get("user_id") or "",
                   payload=record.get("payload") or {})

    def public(self) -> dict:
        return {"id": self.id, "status": self.status, "stage": self.stage,
                "progress": self.progress, "title": self.title,
                "question": self.question, "topic": self.topic,
                "video": self.video, "error": self.error,
                "created": round(self.created, 1),
                "user_id": self.user_id,
                "logs": self.logs[-40:]}


def _read_legacy_thread_file(db_path: Path) -> dict | None:
    """The old single chat-thread.json (possibly sitting exactly where the
    database now lives): read it before SQLite opens the file."""
    if not db_path.is_file() or is_sqlite_file(db_path):
        return None
    try:
        data = json.loads(db_path.read_text(encoding="utf-8"))
        messages = data.get("messages") if isinstance(data, dict) else data
        if not isinstance(messages, list):
            return None
        db_path.unlink()
        return {"messages": [m for m in messages if isinstance(m, dict)]}
    except (OSError, ValueError):
        return None


def _read_legacy_chat_files(root: Path) -> list:
    """The old chats/<id>.json files, read before the database takes over."""
    out = []
    chats_dir = root / "chats"
    if not chats_dir.is_dir():
        return out
    for path in sorted(chats_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        messages = data.get("messages")
        if not isinstance(messages, list):
            continue
        out.append({"id": path.stem,
                    "title": str(data.get("title") or "")[:80],
                    "modified": float(data.get("modified") or 0) or
                                path.stat().st_mtime,
                    "messages": [m for m in messages
                                 if isinstance(m, dict)][:300]})
        path.unlink()
    return out

class RenderServer:
    def __init__(self, frontend: Path, lectures_dir: Path,
                 db_path: Path | None = None, store=None, *,
                 scan_disk: bool | None = None, inline_worker: bool = True):
        self.frontend = Path(frontend).resolve()
        self.lectures_dir = Path(lectures_dir).resolve()
        db_path = Path(db_path).resolve() if db_path else (
            self.lectures_dir.parent / "phiversity.db")

        # a pre-database JSON thread file at the db path (or the legacy
        # chats/ folder next to it) is imported once, then removed
        legacy_thread = _read_legacy_thread_file(db_path)
        legacy_chats = _read_legacy_chat_files(db_path.parent)

        # cloud storage (Supabase) when provided; otherwise the local
        # SQLite file. Disk re-indexing only makes sense on the local
        # backend - in the cloud the index lives in the database and the
        # videos live on Cloudinary.
        self.db = store if store is not None else Database(db_path)
        if scan_disk is None:
            scan_disk = getattr(self.db, "kind", "sqlite") == "sqlite"
        self.scan_disk = scan_disk
        # when the rendering happens in another process (standalone
        # worker), this process reads job state from the store on every
        # poll instead of trusting its in-memory copies
        self.poll_store = not inline_worker
        self.chat_lock = threading.Lock()
        self.jobs: dict[str, Job] = {}
        self.lock = threading.Lock()
        self.queue: queue.Queue = queue.Queue()

        self._restore_jobs()
        self._import_legacy(legacy_thread, legacy_chats)
        self.refresh_lecture_index()

        # the inline worker consumes the in-process queue; a standalone
        # worker (worker.py) polls the store instead and this thread is
        # switched off so only one place renders a given job
        if inline_worker:
            self.worker = threading.Thread(target=self._worker,
                                           daemon=True)
            self.worker.start()

    # -------------------------------------------------- database helpers

    def _restore_jobs(self) -> None:
        """Load every job from the database. Renders that were still
        running when the server stopped are marked interrupted; jobs
        still queued (with their saved request options) are re-enqueued
        so a restart or a standalone worker can pick them up."""
        now = time.time()
        for record in self.db.load_jobs():
            job = Job.from_record(record)
            job.persist = lambda j=job: self.db.save_job(j.to_record())
            if job.status == "queued" and job.payload:
                self.queue.put((job, job.payload))
            elif job.status in ("queued", "running"):
                job.status = "error"
                job.error = ("render was interrupted by a server restart")
                job.log("[error] render was interrupted by a server restart")
                job.persist()
            if now - job.created < 7 * 24 * 3600:
                self.jobs[job.id] = job

    def _import_legacy(self, legacy_thread, legacy_chats) -> None:
        """One-time migration of the JSON era into the database."""
        if self.db.chat_ids():
            return
        if legacy_thread:
            self.db.save_chat("imported",
                              self._chat_title(legacy_thread["messages"]),
                              legacy_thread["messages"])
        for chat in legacy_chats:
            self.db.save_chat(chat["id"], chat["title"],
                              chat["messages"], chat["modified"])

    def refresh_lecture_index(self) -> None:
        """Re-index every lecture on disk into the database (local mode;
        the cloud index is maintained by _on_job_done instead)."""
        if not self.scan_disk:
            return
        on_disk = set()
        for manifest_path in sorted(
                self.lectures_dir.glob("*/manifest.json")):
            try:
                manifest = json.loads(
                    manifest_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            slug = manifest_path.parent.name
            video = manifest_path.parent / "lecture.mp4"
            if not (video.is_file() and SLUG_RE.match(slug)):
                continue
            self.db.upsert_lecture({
                "slug": slug,
                "title": manifest.get("title", slug),
                "question": manifest.get("question"),
                "format": manifest.get("format"),
                "preset": (manifest.get("theme") or {}).get("preset"),
                "segments": len(manifest.get("segments", [])),
                "narration_seconds": sum(
                    s.get("voice_seconds", 0)
                    for s in manifest.get("segments", [])),
                "modified": manifest_path.stat().st_mtime,
                "video": f"/api/lectures/{slug}/video",
            })
            on_disk.add(slug)
        for row in self.db.list_lectures():
            if row["slug"] not in on_disk:
                self.db.delete_lecture(row["slug"])

    # ------------------------------------------------------------- jobs

    def submit(self, payload: dict, user_id: str = "") -> Job | None:
        question = str(payload.get("question") or "").strip()
        topic = str(payload.get("topic") or "").strip()
        if not question and not topic:
            return None
        job = Job(id=uuid.uuid4().hex[:12], question=question,
                  topic=topic, user_id=user_id or "",
                  payload={k: v for k, v in payload.items()
                           if k in ("question", "topic", "quality", "voice",
                                    "tts", "theme", "captions", "transitions",
                                    "max_segments", "render_timeout",
                                    "follow_up_of", "intro_clip")})
        job.persist = lambda: self.db.save_job(job.to_record())
        with self.lock:
            self.jobs[job.id] = job
        self.db.save_job(job.to_record())
        self.queue.put((job, payload))
        return job

    def _worker(self) -> None:
        while True:
            job, payload = self.queue.get()
            self._run_job(job, payload)

    # ------------------------------------------------------ follow-ups

    def _followup_slug(self, follow_of: str) -> str | None:
        """Resolve a finished job (memory first, then the database) to the
        lecture directory its video came from."""
        video = ""
        job = self.jobs.get(follow_of)
        if job is not None and job.status == "done" and job.video:
            video = job.video
        else:
            for record in self.db.load_jobs():
                if record["id"] == follow_of and record.get("video"):
                    video = record["video"]
                    break
        parts = video.strip("/").split("/")
        if len(parts) < 3 or parts[0] != "api" or parts[1] != "lectures":
            return None
        slug = parts[2]
        if not (self.lectures_dir / slug / "manifest.json").is_file():
            return None
        return slug

    def _rebuild_segments(self, slug: str) -> list:
        """Reconstruct the segment list of a finished lecture from its
        manifest and the aligned files in work/segments/."""
        manifest = json.loads(
            (self.lectures_dir / slug / "manifest.json"
             ).read_text(encoding="utf-8"))
        seg_dir = self.lectures_dir / slug / "work" / "segments"
        built = []
        for i, entry in enumerate(manifest.get("segments", [])):
            scene = entry.get("scene") or f"Segment{i}"
            final = seg_dir / f"{scene}.mp4"
            if not final.is_file():
                raise LLMError(
                    f"cannot rebuild {scene}: aligned segment file missing")
            seg = Segment(index=i, scene_name=scene,
                          narration=entry.get("narration", ""),
                          audio_duration=float(
                              entry.get("voice_seconds", 0) or 0),
                          final=final, pre_aligned=True)
            seg.visual = {"transition":
                          entry.get("transition") or "carry-over"}
            built.append(seg)
        if not built:
            raise LLMError("the previous lecture has no segments")
        return built

    def _build_config(self, job: Job, payload: dict, *, max_segments: int,
                      captions: bool, theme: str) -> PipelineConfig:
        """Pipeline settings shared by fresh and follow-up renders."""
        return PipelineConfig(
            question=job.question,
            out_dir=self.lectures_dir,
            max_segments=int(payload.get("max_segments") or max_segments),
            captions=captions,
            theme=str(payload.get("theme") or theme),
            transitions=str(payload.get("transitions") or "none"),
            tts=TTSConfig(engine=str(payload.get("tts") or "edge"),
                          voice=str(payload.get("voice")
                                   or "en-US-AriaNeural")),
            render=RenderConfig(quality=str(payload.get("quality") or "m"),
                                 timeout=float(payload.get("render_timeout")
                                               or 420.0),
                                 heal_attempts=2),
        )

    def _run_followup_job(self, job: Job, payload: dict, slug: str) -> None:
        """Extend an existing lecture with new segments answering the
        follow-up question, then re-stitch the full video."""
        job.log(f"[follow-up] extending the lecture '{slug}' with your "
                f"follow-up question")
        manifest = json.loads(
            (self.lectures_dir / slug / "manifest.json"
             ).read_text(encoding="utf-8"))
        cfg = self._build_config(
            job, payload, max_segments=3, captions=False,
            theme=(manifest.get("theme") or {}).get("preset") or "auto")
        if not cfg.llm.api_key and "localhost" not in cfg.llm.base_url \
                and "127.0.0.1" not in cfg.llm.base_url:
            raise LLMError("follow-up questions need an LLM API key "
                           "(LLM_API_KEY in .env)")
        client = LLMClient(cfg.llm)
        pipeline = Pipeline(cfg, client, log=job.log)
        pipeline.title = manifest.get("title", slug)
        pipeline.lesson_format = manifest.get("format") or "conceptual"
        pipeline.out_dir = self.lectures_dir / slug
        pipeline.work_dir = pipeline.out_dir / "work"
        built = self._rebuild_segments(slug)
        segments = pipeline.followup(job.question, built)
        result = pipeline._compose(segments)
        job.title = result.title
        job.video = f"/api/lectures/{slug}/video"
        job.status = "done"
        self.refresh_lecture_index()

    def get_job(self, job_id: str) -> Job | None:
        if self.poll_store:
            try:
                record = self.db.load_job(job_id)
            except Exception:  # noqa: BLE001 - storage hiccup -> not found
                return None
            return Job.from_record(record) if record else None
        return self.jobs.get(job_id)

    def list_jobs(self) -> list:
        if self.poll_store:
            try:
                records = sorted(self.db.load_jobs(),
                                 key=lambda r: -r["created"])
            except Exception:  # noqa: BLE001
                records = []
            return [Job.from_record(record).public()
                    for record in records]
        return [job.public() for job in
                sorted(self.jobs.values(), key=lambda j: -j.created)]

    def _run_job(self, job: Job, payload: dict) -> None:
        job.status = "running"
        job.persist()
        job.log("[queue] job accepted - configuring the pipeline")
        cfg = self._build_config(
            job, payload, max_segments=5,
            captions=bool(payload.get("captions", False)), theme="auto")
        if job.topic:
            cfg.demo = job.topic
        # auto-detect the brand intro clip, exactly like the CLI does
        intro = payload.get("intro_clip")
        if intro is None:
            intro = ("Intro.mp4" if (self.lectures_dir.parent /
                                    "Intro.mp4").is_file() else None)
        cfg.intro_clip = str(intro) if intro else None
        follow_of = str(payload.get("follow_up_of") or "").strip()
        try:
            if follow_of:
                slug = self._followup_slug(follow_of)
                if slug:
                    self._run_followup_job(job, payload, slug)
                    self._on_job_done(job, None, slug)
                    return
                job.log("[follow-up] previous lecture not found or was "
                        "deleted - generating a fresh lecture instead")
            result = run_pipeline(cfg, log=job.log)
            job.title = result.title
            slug = result.final_video.parent.name
            job.video = f"/api/lectures/{slug}/video"
            job.status = "done"
            self.refresh_lecture_index()
            self._on_job_done(job, result.final_video, slug)
        except Exception as exc:  # noqa: BLE001 - surfaced to the UI
            job.status = "error"
            job.error = str(exc)
            job.log(f"[error] {exc}")
        job.persist()

    def _on_job_done(self, job: Job, final_video: Path | None,
                     slug: str) -> None:
        """Finished render housekeeping. In the cloud the video is
        uploaded to Cloudinary (the backend disk is ephemeral), the
        lecture index row gets the permanent URL, and a row lands in the
        spec-shaped videos table. Locally everything stays on disk."""
        if job.status != "done":
            return
        manifest = {}
        manifest_path = self.lectures_dir / slug / "manifest.json"
        try:
            if manifest_path.is_file():
                manifest = json.loads(
                    manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            manifest = {}
        if cloudinary_configured() and final_video is not None:
            public_id = f"phiversity/{slug}/lecture"
            try:
                job.log("[upload] copying the finished video to Cloudinary")
                uploaded = upload_video(final_video, public_id)
                job.video = uploaded["url"]
                job.log(f"[upload] done: {job.video}")
                duration = uploaded.get("duration") or 0
                try:
                    from .tts import ffprobe_duration
                    duration = duration or ffprobe_duration(final_video)
                except Exception:  # noqa: BLE001 - metadata only
                    pass
                try:
                    self.db.add_video(job.id, uploaded["url"],
                                      uploaded.get("thumbnail_url", ""),
                                      duration)
                except Exception as exc:  # noqa: BLE001
                    job.log(f"[upload] could not record the video row: {exc}")
            except Exception as exc:  # noqa: BLE001 - keep the local copy
                job.log(f"[upload] Cloudinary upload failed ({exc}); "
                        f"serving the local copy while it exists")
        if manifest or not self.scan_disk:
            self.db.upsert_lecture({
                "slug": slug,
                "title": manifest.get("title") or job.title or slug,
                "question": manifest.get("question"),
                "format": manifest.get("format"),
                "preset": (manifest.get("theme") or {}).get("preset"),
                "segments": len(manifest.get("segments", [])),
                "narration_seconds": sum(
                    s.get("voice_seconds", 0)
                    for s in manifest.get("segments", [])),
                "modified": time.time(),
                "video": job.video or f"/api/lectures/{slug}/video",
            })
        job.persist()

    # ------------------------------------------------- saved chat threads

    @staticmethod
    def _chat_title(messages: list) -> str:
        for message in messages:
            if isinstance(message, dict) and message.get("role") == "user" \
                    and message.get("text"):
                return str(message["text"])[:80]
        return "Untitled chat"

    def list_chats(self) -> list:
        """Summaries of every saved chat, newest first, with the video
        references generated inside each conversation."""
        now = time.time()
        out = []
        for chat in self.db.list_chats():
            messages = chat["messages"]
            out.append({
                "id": chat["id"],
                "title": chat["title"] or self._chat_title(messages),
                "modified": chat["modified"],
                "messages": len(messages),
                "videos": [{"title": m.get("title") or "",
                            "video": m.get("video")}
                           for m in messages
                           if isinstance(m, dict)
                           and m.get("kind") == "job"
                           and m.get("status") == "done"
                           and m.get("video")],
                "ago": now - chat["modified"],
            })
        return sorted(out, key=lambda chat: -chat["modified"])

    def load_chat_by_id(self, chat_id: str) -> dict | None:
        chat = self.db.load_chat(chat_id)
        if not chat:
            return None
        return {"id": chat["id"],
                "title": chat["title"] or self._chat_title(
                    chat["messages"]),
                "modified": chat["modified"],
                "messages": chat["messages"][:300]}

    def save_chat_by_id(self, chat_id: str, payload: dict) -> bool:
        if not SLUG_RE.match(chat_id or ""):
            return False
        messages = payload.get("messages")
        if not isinstance(messages, list):
            return False
        title = str(payload.get("title") or "")[:80]
        return self.db.save_chat(chat_id,
                                 title or self._chat_title(messages),
                                 [m for m in messages
                                  if isinstance(m, dict)][:300])

    def delete_chat_by_id(self, chat_id: str) -> bool:
        return self.db.delete_chat(chat_id)

    # ------------------------------------------------------------- lectures

    @staticmethod
    def llm_configured() -> bool:
        load_env_file()
        return bool(LLMConfig.from_env().api_key)

    def topics(self) -> tuple:
        configured = self.llm_configured()
        return [{"topic": topic,
                 "title": BUNDLED_LECTURES[topic]["title"],
                 "format": BUNDLED_LECTURES[topic].get("format",
                                                       "conceptual")}
                for topic in bundled_topics()], configured

    def list_lectures(self) -> list:
        return self.db.list_lectures()

    # ------------------------------------------------- search / status

    def search(self, query: str) -> list:
        """Lectures matching a text query (title, question, format, slug)."""
        import unicodedata

        def norm(text: str) -> str:
            return unicodedata.normalize(
                "NFKD", text or "").lower()

        needle = norm(query).strip()
        if not needle:
            return self.list_lectures()
        words = needle.split()
        hits = []
        for lecture in self.list_lectures():
            haystack = norm(" ".join(
                [lecture["title"], lecture["question"] or "",
                 lecture["format"] or "", lecture["slug"]]))
            if all(word in haystack for word in words):
                hits.append(lecture)
        return hits

    def status(self) -> dict:
        from datetime import datetime, timezone
        import shutil
        return {
            "server": "ok",
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "llm_configured": self.llm_configured(),
            "sample_lectures": len(bundled_topics()),
            "generated_lectures": len(self.list_lectures()),
            "jobs": len(self.jobs),
            "ffmpeg": shutil.which("ffmpeg") is not None,
            "manim": shutil.which("manim") is not None,
            "database": str(self.db.path),
            "store": getattr(self.db, "kind", "sqlite"),
            "cdn": "cloudinary" if cloudinary_configured() else "local-disk",
        }

    def delete_lecture(self, slug: str) -> bool:
        """Remove a generated lecture directory (validated slug only).
        In the cloud the Cloudinary copy is destroyed as well."""
        import shutil
        if not SLUG_RE.match(slug):
            return False
        target = (self.lectures_dir / slug).resolve()
        if not str(target).startswith(str(self.lectures_dir.resolve())):
            return False
        if target.is_dir():
            shutil.rmtree(target)
        elif self.scan_disk:
            return False   # local mode: a missing directory is a 404
        elif not any(lec["slug"] == slug for lec in self.db.list_lectures()):
            return False   # cloud mode: no stored lecture with that slug
        if cloudinary_configured():
            try:
                destroy(f"phiversity/{slug}/lecture")
            except Exception:  # noqa: BLE001 - removal is best-effort
                pass
        self.db.delete_lecture(slug)
        with self.lock:
            for job in self.jobs.values():
                if job.video == f"/api/lectures/{slug}/video":
                    job.video = ""
                    if job.persist is not None:
                        job.persist()
        return True

    # ------------------------------------------------------------ static

    def resolve_static(self, path: str) -> Path | None:
        from urllib.parse import unquote
        rel = unquote(path).lstrip("/") or "index.html"
        if rel.endswith("/"):
            rel += "index.html"
        root = self.frontend.resolve()
        target = (root / rel).resolve()
        if not target.is_relative_to(root):
            return None
        return target if target.is_file() else None

    def resolve_video(self, slug: str) -> Path | None:
        if not SLUG_RE.match(slug):
            return None
        video = self.lectures_dir / slug / "lecture.mp4"
        return video if video.is_file() else None


def make_handler(server: RenderServer):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *args):  # quiet
            pass

        # ------------------------------------------------------ plumbing

        def _json(self, obj, code=200):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict:
            length = int(self.headers.get("Content-Length") or 0)
            if length > 1_000_000:
                self.close_connection = True  # body left unread
                return {}
            if length <= 0:
                return {}
            try:
                return json.loads(self.rfile.read(length) or b"{}")
            except ValueError:
                return {}

        def _same_origin(self) -> bool:
            """Reject browser requests that another website initiated
            against this server (CSRF / DNS-rebinding)."""
            from urllib.parse import urlparse
            host = self.headers.get("Host", "")
            origin = self.headers.get("Origin")
            return origin is None or urlparse(origin).netloc == host

        # --------------------------------------------------------- routes

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path == "/api/config":
                topics, llm_configured = server.topics()
                return self._json({
                    "llm_configured": llm_configured,
                    "topics": topics,
                    "themes": ["auto", "math", "lab", "spatial", "data",
                               "paper"],
                    "voices": ["en-US-AriaNeural", "en-US-GuyNeural",
                               "en-GB-SoniaNeural", "hi-IN-SwaraNeural"],
                    "qualities": ["l", "m", "h"],
                    "tts_engines": ["edge", "gtts", "silence"],
                    "transitions": ["none", "flip"],
                })
            if path == "/api/jobs":
                return self._json({"jobs": server.list_jobs()})
            if path.startswith("/api/jobs/"):
                job = server.get_job(path.split("/")[-1])
                if not job:
                    return self._json({"error": "no such job"}, 404)
                return self._json(job.public())
            if path == "/api/lectures":
                return self._json({"lectures":
                                   sorted(server.list_lectures(),
                                          key=lambda lec: -lec["modified"])})
            if path == "/api/search":
                from urllib.parse import parse_qs, urlparse
                query = parse_qs(urlparse(self.path).query).get("q", [""])[0]
                return self._json({"lectures": server.search(query),
                                   "query": query})
            if path == "/api/status":
                return self._json(server.status())
            if path == "/api/chats":
                return self._json({"chats": server.list_chats()})
            if path.startswith("/api/chats/"):
                parts = path.split("/")
                chat_id = parts[3] if len(parts) > 3 else ""
                if not chat_id or (len(parts) > 4 and parts[4]):
                    return self._json({"error": "no such chat"}, 404)
                chat = server.load_chat_by_id(chat_id)
                if not chat:
                    return self._json({"error": "no such chat"}, 404)
                return self._json(chat)
            if path.startswith("/api/lectures/") and path.endswith("/video"):
                slug = path.split("/")[3]
                return self._send_video(server.resolve_video(slug))
            return self._send_static(path)

        def do_DELETE(self):
            path = self.path.split("?", 1)[0]
            if not self._same_origin():
                return self._json({"error": "cross-origin request"}, 403)
            if path.startswith("/api/chats/"):
                parts = path.split("/")
                chat_id = parts[3] if len(parts) > 3 else ""
                if not chat_id or (len(parts) > 4 and parts[4]):
                    return self._json({"error": "no such chat"}, 404)
                if server.delete_chat_by_id(chat_id):
                    return self._json({"ok": True})
                return self._json({"error": "no such chat"}, 404)
            if not path.startswith("/api/lectures/") or path.endswith("/video"):
                return self._json({"error": "not found"}, 404)
            slug = path.split("/")[3]
            if server.delete_lecture(slug):
                return self._json({"deleted": slug})
            return self._json({"error": "no such lecture"}, 404)

        def do_POST(self):
            path = self.path.split("?", 1)[0]
            if not self._same_origin():
                return self._json({"error": "cross-origin request"}, 403)
            if path.startswith("/api/chats/"):
                parts = path.split("/")
                chat_id = parts[3] if len(parts) > 3 else ""
                if not chat_id or (len(parts) > 4 and parts[4]):
                    return self._json({"error": "invalid chat"}, 400)
                payload = self._read_json()
                if not server.save_chat_by_id(chat_id, payload):
                    return self._json({"error": "invalid chat"}, 400)
                return self._json({"ok": True, "id": chat_id})
            if path not in ("/api/generate", "/api/run"):
                return self._json({"error": "not found"}, 404)
            payload = self._read_json()
            topic = str(payload.get("topic") or "").strip()
            if topic:
                try:
                    payload["topic"] = normalize_topic(topic)
                except ValueError as exc:
                    return self._json({"error": str(exc)}, 400)
            job = server.submit(payload)
            if not job:
                return self._json({"error": "provide a question or a topic"},
                                  400)
            return self._json({"id": job.id, "job": job.public()}, 202)

        # ---------------------------------------------------------- files

        def _send_static(self, path: str):
            target = server.resolve_static(path)
            if target is None:
                # fall back to the landing page for extension-less app
                # routes only; a missing asset or API path is a real 404
                if "." in path.rsplit("/", 1)[-1] or path.startswith("/api/"):
                    return self._json({"error": "not found"}, 404)
                target = server.resolve_static("index.html")
                if target is None:
                    return self._json({"error": "not found"}, 404)
            self._send_file(target)

        def _send_video(self, video: Path | None):
            if video is None:
                return self._json({"error": "no such lecture"}, 404)
            self._send_file(video, video=True)

        def _send_file(self, target: Path, video: bool = False):
            total = target.stat().st_size
            ctype = (mimetypes.guess_type(str(target))[0]
                     or "application/octet-stream")
            header = self.headers.get("Range") if video else None
            if header:
                match = re.match(r"bytes=(\d*)-(\d*)$", header)
                first, last = (match.groups() if match else ("", ""))
                if first:
                    start = int(first)
                    end = min(int(last), total - 1) if last else total - 1
                elif last:  # suffix range: the final N bytes
                    start = max(total - int(last), 0)
                    end = total - 1
                else:
                    start, end = 0, total - 1
                if start > end or start >= total:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{total}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                length = end - start + 1
                self.send_response(206)
                self.send_header("Content-Range",
                                 f"bytes {start}-{end}/{total}")
            else:
                start, end, length = 0, total - 1, total
                self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(length))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            with target.open("rb") as fh:
                fh.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = fh.read(min(65536, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)

    return Handler


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="phiversity-serve",
        description="Serve the Phiversity frontend and the lecture "
                    "generation API locally.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--root", default=".", metavar="DIR",
                        help="workspace root holding Frontend/ and "
                             "lectures/ (default: current directory)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    frontend = root / "Frontend"
    lectures = (Path(os.environ["PHIVERSITY_OUT_DIR"]).resolve()
                if os.environ.get("PHIVERSITY_OUT_DIR") else root / "lectures")
    if not frontend.is_dir():
        raise SystemExit(f"no frontend found at {frontend}")
    lectures.mkdir(parents=True, exist_ok=True)

    server = RenderServer(frontend, lectures, root / "phiversity.db")
    httpd = ThreadingHTTPServer((args.host, args.port),
                                make_handler(server))
    print(f"Phiversity server  ->  http://{args.host}:{args.port}")
    print(f"frontend: {frontend}")
    print(f"lectures: {lectures}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nserver stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
