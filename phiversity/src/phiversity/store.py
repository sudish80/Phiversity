"""Storage backends for Phiversity.

Two interchangeable backends behind the same interface used by
``server.RenderServer``:

* ``SqliteStore``    — the local default (wraps ``db.Database``, plus
  ``user_id`` / ``payload`` columns and a spec-shaped ``videos`` table).
* ``SupabaseStore``  — Supabase Postgres via its REST layer (PostgREST),
  using the service-role key. Server-side only: the service key must
  never reach the browser or the frontend.

The backend is chosen by ``open_store``: if ``SUPABASE_URL`` and
``SUPABASE_SERVICE_KEY`` are set, cloud storage is used; otherwise the
local SQLite file. No other code has to know which is active.
"""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from .db import Database

MAX_LOG_LINES = 400


class StoreError(RuntimeError):
    """Raised when a cloud storage call fails after retries."""


def open_store(root: str | Path):
    """Return the configured backend: Supabase when the env vars exist,
    otherwise SQLite in the workspace root."""
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    if url and key:
        return SupabaseStore(url, key)
    return SqliteStore(Path(root) / "phiversity.db")


def _iso(epoch: float) -> str:
    return datetime.fromtimestamp(float(epoch or time.time()),
                                  timezone.utc).isoformat()


def _epoch(value: str) -> float:
    try:
        return datetime.fromisoformat(str(value)).timestamp()
    except (ValueError, TypeError):
        return time.time()


class SqliteStore:
    """Local SQLite backend. Mirrors ``db.Database`` and persists the two
    newer job fields (``user_id``, ``payload``) plus the spec-shaped
    ``videos`` table."""

    kind = "sqlite"

    def __init__(self, path: str | Path):
        self.db = Database(path)
        self.path = self.db.path
        with self.db.lock:
            for column, ddl in (("user_id", "TEXT NOT NULL DEFAULT ''"),
                                ("payload", "TEXT NOT NULL DEFAULT '{}'")):
                try:
                    self.db.conn.execute(
                        f"ALTER TABLE jobs ADD COLUMN {column} {ddl}")
                    self.db.conn.commit()
                except Exception:  # noqa: BLE001 - already migrated
                    pass
            self.db.conn.executescript("""
                CREATE TABLE IF NOT EXISTS videos (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id        TEXT NOT NULL,
                    video_url     TEXT NOT NULL DEFAULT '',
                    thumbnail_url TEXT NOT NULL DEFAULT '',
                    duration      REAL NOT NULL DEFAULT 0,
                    created_at    REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS videos_job_idx
                    ON videos(job_id);
            """)
            self.db.conn.commit()

    def close(self) -> None:
        self.db.close()

    # ------------------------------------------------------------- jobs

    def save_job(self, record: dict) -> None:
        with self.db.lock:
            self.db.conn.execute(
                """INSERT INTO jobs (id, created, status, stage, progress,
                   title, question, topic, video, error, logs,
                   user_id, payload)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET
                     status=excluded.status, stage=excluded.stage,
                     progress=excluded.progress, title=excluded.title,
                     question=excluded.question, topic=excluded.topic,
                     video=excluded.video, error=excluded.error,
                     logs=excluded.logs, user_id=excluded.user_id,
                     payload=excluded.payload""",
                (record["id"], record["created"], record["status"],
                 record.get("stage", "-"), int(record.get("progress", 0)),
                 record.get("title", ""), record.get("question", ""),
                 record.get("topic", ""), record.get("video", ""),
                 record.get("error", ""),
                 json.dumps(record.get("logs", [])[-MAX_LOG_LINES:]),
                 record.get("user_id", ""),
                 json.dumps(record.get("payload", {}) or {})))
            self.db.conn.commit()

    def load_jobs(self) -> list:
        with self.db.lock:
            rows = self.db.conn.execute(
                """SELECT id, created, status, stage, progress, title,
                   question, topic, video, error, logs, user_id, payload
                   FROM jobs ORDER BY created""").fetchall()
        records = []
        for row in rows:
            records.append({"id": row[0], "created": row[1],
                            "status": row[2], "stage": row[3],
                            "progress": row[4], "title": row[5],
                            "question": row[6], "topic": row[7],
                            "video": row[8], "error": row[9],
                            "logs": _load_json(row[10], []),
                            "user_id": row[11] or "",
                            "payload": _load_json(row[12], {})})
        return records

    def load_job(self, job_id: str) -> dict | None:
        for record in self.load_jobs():
            if record["id"] == job_id:
                return record
        return None

    # ------------------------------------------------------------ chats

    def save_chat(self, chat_id: str, title: str, messages: list,
                  modified: float | None = None) -> bool:
        return self.db.save_chat(chat_id, title, messages, modified)

    def load_chat(self, chat_id: str) -> dict | None:
        return self.db.load_chat(chat_id)

    def chat_ids(self) -> list:
        return self.db.chat_ids()

    def list_chats(self) -> list:
        return self.db.list_chats()

    def delete_chat(self, chat_id: str) -> bool:
        return self.db.delete_chat(chat_id)

    # --------------------------------------------------------- lectures

    def upsert_lecture(self, record: dict) -> None:
        self.db.upsert_lecture(record)

    def delete_lecture(self, slug: str) -> None:
        self.db.delete_lecture(slug)

    def list_lectures(self) -> list:
        return self.db.list_lectures()

    # ----------------------------------------------------------- videos

    def add_video(self, job_id: str, video_url: str,
                  thumbnail_url: str = "", duration: float = 0.0) -> str:
        with self.db.lock:
            cursor = self.db.conn.execute(
                """INSERT INTO videos (job_id, video_url, thumbnail_url,
                   duration, created_at) VALUES (?,?,?,?,?)""",
                (job_id, video_url, thumbnail_url, float(duration or 0),
                 time.time()))
            self.db.conn.commit()
            return str(cursor.lastrowid)

    def claim_next_queued(self) -> dict | None:
        """Claim one queued job (single-process semantics: the inline
        queue is not used by the standalone worker against SQLite)."""
        for record in self.load_jobs():
            if record["status"] == "queued" and record.get("payload"):
                record["status"] = "running"
                self.save_job(record)
                return record
        return None


class SupabaseStore:
    """Supabase Postgres over its REST API (PostgREST), with the
    service-role key. Same call surface as ``SqliteStore``.

    Tables (see supabase/schema.sql): jobs, chats, lectures, videos,
    users. The service key bypasses Row Level Security, which exists to
    protect direct client access — never ship this key to a browser.
    """

    kind = "supabase"

    def __init__(self, url: str, service_key: str, timeout: float = 25.0):
        self.url = url.rstrip("/")
        self.key = service_key
        self.timeout = timeout
        self.path = f"supabase:{self.url}"
        self._lock = threading.Lock()

    # ------------------------------------------------------------ REST

    def _rest(self, method: str, path: str, *, params: dict | None = None,
              body=None, prefer: str | None = None):
        query = ""
        if params:
            query = "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        url = f"{self.url}/rest/v1/{path.lstrip('/')}{query}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        last_error: Exception | None = None
        for attempt in range(2):
            request = urllib.request.Request(url, data=data, method=method,
                                             headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) \
                        as response:
                    text = response.read().decode("utf-8")
                    if not text:
                        return None
                    try:
                        return json.loads(text)
                    except ValueError:
                        return None
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:300]
                if 500 <= exc.code and attempt == 0:
                    last_error = StoreError(
                        f"supabase {method} {path} -> {exc.code}: {detail}")
                    time.sleep(0.8)
                    continue
                raise StoreError(
                    f"supabase {method} {path} -> {exc.code}: {detail}") \
                    from None
            except (urllib.error.URLError, OSError) as exc:
                if attempt == 0:
                    last_error = StoreError(
                        f"supabase {method} {path} unreachable: {exc}")
                    time.sleep(0.8)
                    continue
                raise StoreError(
                    f"supabase {method} {path} unreachable: {exc}") from exc
        raise last_error or StoreError(f"supabase {method} {path} failed")

    @staticmethod
    def _upsert(path: str, rows: list, *, on_conflict: str) -> None:
        SupabaseStore._rest(
            None, "POST", f"{path}", params={"on_conflict": on_conflict},
            body=rows, prefer="resolution=merge-duplicates,return=minimal")

    # ------------------------------------------------------------- jobs

    @staticmethod
    def _job_to_row(record: dict) -> dict:
        return {
            "id": record["id"],
            "user_id": record.get("user_id") or None,
            "status": record.get("status", "queued"),
            "stage": record.get("stage", "-"),
            "progress": int(record.get("progress", 0)),
            "title": record.get("title", ""),
            "question": record.get("question", ""),
            "topic": record.get("topic", ""),
            "video": record.get("video", ""),
            "error_message": record.get("error", ""),
            "logs": list(record.get("logs", []) or [])[-MAX_LOG_LINES:],
            "payload": record.get("payload", {}) or {},
            "created_at": _iso(record.get("created")),
            "updated_at": _iso(time.time()),
        }

    @staticmethod
    def _row_to_job(row: dict) -> dict:
        return {
            "id": row["id"],
            "created": _epoch(row.get("created_at")),
            "status": row.get("status", "queued"),
            "stage": row.get("stage", "-"),
            "progress": int(row.get("progress", 0)),
            "title": row.get("title", ""),
            "question": row.get("question", ""),
            "topic": row.get("topic", ""),
            "video": row.get("video", ""),
            "error": row.get("error_message", ""),
            "logs": row.get("logs", []) or [],
            "user_id": row.get("user_id") or "",
            "payload": row.get("payload", {}) or {},
        }

    def save_job(self, record: dict) -> None:
        self._upsert("jobs", [self._job_to_row(record)], on_conflict="id")

    def load_jobs(self) -> list:
        rows = self._rest("GET", "jobs",
                          params={"order": "created.asc", "limit": "1000"})
        return [self._row_to_job(row) for row in (rows or [])]

    def load_job(self, job_id: str) -> dict | None:
        rows = self._rest("GET", "jobs", params={"id": f"eq.{job_id}",
                                                 "limit": "1"})
        return self._row_to_job(rows[0]) if rows else None

    def claim_next_queued(self) -> dict | None:
        """Atomically claim one queued job: select the oldest queued row,
        then flip queued->running with the same filter, so two workers
        cannot claim the same job. Returns the claimed record."""
        rows = self._rest("GET", "jobs",
                          params={"status": "eq.queued",
                                  "order": "created.asc", "limit": "1"})
        if not rows:
            return None
        job_id = rows[0]["id"]
        claimed = self._rest(
            None, "PATCH", "jobs",
            params={"id": f"eq.{job_id}", "status": "eq.queued"},
            body={"status": "running", "updated_at": _iso(time.time())},
            prefer="return=representation")
        if claimed:
            return self._row_to_job(claimed[0])
        return None

    # ------------------------------------------------------------ chats

    @staticmethod
    def _chat_row(chat_id: str, title: str, messages: list,
                  modified: float | None) -> dict:
        return {"id": chat_id, "title": title[:80],
                "modified": _iso(modified or time.time()),
                "messages": [m for m in messages if isinstance(m, dict)][:300]}

    @staticmethod
    def _chat_record(row: dict) -> dict:
        return {"id": row["id"], "title": row.get("title", ""),
                "modified": _epoch(row.get("modified")),
                "messages": row.get("messages", []) or []}

    def save_chat(self, chat_id: str, title: str, messages: list,
                  modified: float | None = None) -> bool:
        if not isinstance(messages, list):
            return False
        self._upsert("chats", [self._chat_row(chat_id, title, messages,
                                              modified)],
                     on_conflict="id")
        return True

    def load_chat(self, chat_id: str) -> dict | None:
        rows = self._rest("GET", "chats", params={"id": f"eq.{chat_id}",
                                                        "limit": "1"})
        return self._chat_record(rows[0]) if rows else None

    def chat_ids(self) -> list:
        rows = self._rest("GET", "chats", params={"select": "id"})
        return [row["id"] for row in (rows or [])]

    def list_chats(self) -> list:
        rows = self._rest("GET", "chats",
                          params={"order": "modified.desc", "limit": "500"})
        return [self._chat_record(row) for row in (rows or [])]

    def delete_chat(self, chat_id: str) -> bool:
        result = self._rest("DELETE", "chats",
                            params={"id": f"eq.{chat_id}"})
        return True  # PostgREST returns no rows to count on minimal delete

    # --------------------------------------------------------- lectures

    @staticmethod
    def _lecture_row(record: dict) -> dict:
        return {
            "slug": record["slug"],
            "title": record.get("title", ""),
            "question": record.get("question"),
            "format": record.get("format"),
            "preset": record.get("preset"),
            "segments": int(record.get("segments", 0)),
            "narration_seconds": float(record.get("narration_seconds", 0)),
            "modified": _iso(record.get("modified")),
            "video": record.get("video", ""),
        }

    @staticmethod
    def _lecture_record(row: dict) -> dict:
        return {
            "slug": row["slug"],
            "title": row.get("title", ""),
            "question": row.get("question"),
            "format": row.get("format"),
            "preset": row.get("preset"),
            "segments": int(row.get("segments", 0) or 0),
            "narration_seconds": float(row.get("narration_seconds", 0) or 0),
            "modified": _epoch(row.get("modified")),
            "video": row.get("video", ""),
        }

    def upsert_lecture(self, record: dict) -> None:
        self._upsert("lectures", [self._lecture_row(record)],
                     on_conflict="slug")

    def delete_lecture(self, slug: str) -> None:
        self._rest("DELETE", "lectures", params={"slug": f"eq.{slug}"})

    def list_lectures(self) -> list:
        rows = self._rest("GET", "lectures",
                          params={"order": "modified.desc", "limit": "500"})
        return [self._lecture_record(row) for row in (rows or [])]

    # ----------------------------------------------------------- videos

    def add_video(self, job_id: str, video_url: str,
                  thumbnail_url: str = "", duration: float = 0.0) -> str:
        rows = self._rest(
            None, "POST", "videos",
            body={"job_id": job_id, "video_url": video_url,
                  "thumbnail_url": thumbnail_url,
                  "duration": float(duration or 0)},
            prefer="return=representation")
        return (rows[0].get("id") if rows else "") or ""

    # ------------------------------------------------------------ users

    def ensure_user(self, user_id: str, email: str = "") -> None:
        """Mirror an authenticated user into public.users (upsert)."""
        if not user_id:
            return
        self._upsert("users", [{"id": user_id, "email": email}],
                     on_conflict="id")


def _load_json(text, default):
    try:
        return json.loads(text) if isinstance(text, str) else (text or default)
    except (ValueError, TypeError):
        return default
