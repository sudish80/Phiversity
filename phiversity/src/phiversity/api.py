"""Cloud API for Phiversity: FastAPI wrapper around the render server.

Same JSON API as the local stdlib server (plus the deployment spec
routes), backed by the pluggable storage layer:

  GET    /health                     deployment probe (Render health check)
  POST   /api/run                    start a job: {question? | topic?,
                                     quality?, voice?, tts?, theme?,
                                     captions?, transitions?, max_segments?}
         /api/generate               alias kept for the existing frontend
  GET    /api/jobs                   job list
  GET    /api/jobs/{job_id}          status, stage, progress, live log tail
  GET    /api/lectures               generated lectures
  GET    /api/lectures/{slug}/video  local file, or 307 -> Cloudinary URL
  DELETE /api/lectures/{slug}
  GET/POST/DELETE /api/chats[/{id}]
  GET    /api/config | /api/search | /api/status

Deployment wiring (all secrets are server-side env vars only):
  SUPABASE_URL / SUPABASE_SERVICE_KEY / SUPABASE_ANON_KEY
      -> Postgres storage via store.SupabaseStore; bearer tokens from the
         frontend are verified against Supabase Auth (GoTrue) and the
         resolved user id is stamped onto jobs. Passwords never touch us.
  CLOUDINARY_* -> finished videos are uploaded to Cloudinary; the local
         copy is a temporary cache on the (ephemeral) disk.
  ALLOWED_ORIGINS -> comma-separated CORS allowlist, "*" for a public API.

Run:  uvicorn phiversity.api:app --host 0.0.0.0 --port $PORT
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from .config import load_env_file
from .media import cloudinary_configured
from .server import RenderServer
from .store import StoreError, open_store
from .templates import normalize_topic


def create_app(root: str | Path | None = None) -> FastAPI:
    load_env_file()
    root = Path(root or os.environ.get("PHIVERSITY_ROOT") or ".").resolve()
    frontend = root / "Frontend"
    lectures = (Path(os.environ["PHIVERSITY_OUT_DIR"]).resolve()
                if os.environ.get("PHIVERSITY_OUT_DIR")
                else root / "lectures")
    lectures.mkdir(parents=True, exist_ok=True)

    store = open_store(root)
    inline_worker = os.environ.get("PHIVERSITY_INLINE_WORKER", "1") != "0"
    server = RenderServer(frontend, lectures, store=store,
                          inline_worker=inline_worker)

    allowed_raw = os.environ.get("ALLOWED_ORIGINS", "").strip()
    if not allowed_raw or allowed_raw == "*":
        allowed = "*"
    else:
        allowed = [o.strip().rstrip("/") for o in allowed_raw.split(",")
                   if o.strip()]

    app = FastAPI(title="Phiversity API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allowed == "*" else allowed,
        allow_credentials=False,        # bearer tokens, not cookies
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Range", "Accept-Ranges", "Location"],
        max_age=86400,
    )

    # ------------------------------------------------------------- guards

    def _origin_ok(request: Request) -> bool:
        """Same protection as the local server: browsers may only call
        with an Origin we allow (blocks other sites' pages from driving
        the API). Non-browser requests carry no Origin header."""
        origin = request.headers.get("Origin")
        if origin is None:
            return True
        if allowed == "*":
            return True
        return origin.rstrip("/") in allowed

    @app.middleware("http")
    async def origin_guard(request: Request, call_next):
        if request.method in ("POST", "DELETE", "PUT", "PATCH"):
            if not _origin_ok(request):
                return JSONResponse({"error": "cross-origin request"}, 403)
        return await call_next(request)

    def _err(code: int, message: str) -> JSONResponse:
        return JSONResponse({"error": message}, status_code=code)

    def _safe(call):
        """Storage failures surface as a clean 503, not a stack trace."""
        try:
            return call()
        except StoreError as exc:
            return JSONResponse({"error": f"storage unavailable: {exc}"},
                                status_code=503)

    # --------------------------------------------------------------- auth

    def _user(request: Request) -> tuple[str, str]:
        """Resolve a Supabase Auth bearer token to (user_id, email).
        Returns ("", "") when absent/invalid; never rejects the request -
        anonymous use stays possible."""
        header = request.headers.get("Authorization", "")
        token = header[7:].strip() if header.lower().startswith(
            "bearer ") else ""
        if not token:
            return "", ""
        base = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
        key = (os.environ.get("SUPABASE_ANON_KEY", "").strip()
               or os.environ.get("SUPABASE_SERVICE_KEY", "").strip())
        if not base or not key:
            return "", ""
        request_ = Request(
            f"{base}/auth/v1/user", method="GET",
            headers={"apikey": key, "Authorization": f"Bearer {token}"})
        try:
            with urlopen(request_, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError):
            return "", ""
        return str(data.get("id") or ""), str(data.get("email") or "")

    # -------------------------------------------------------------- routes

    @app.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "service": "phiversity",
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "store": getattr(server.db, "kind", "sqlite"),
            "cdn": "cloudinary" if cloudinary_configured() else "local-disk",
            "llm_configured": server.llm_configured(),
        }

    @app.get("/")
    def index() -> dict:
        return {"service": "phiversity",
                "api": ["/health", "/api/run", "/api/jobs", "/api/lectures",
                        "/api/config", "/api/status"]}

    def _start_job(payload: dict, request: Request) -> Response:
        topic = str(payload.get("topic") or "").strip()
        if topic:
            try:
                payload["topic"] = normalize_topic(topic)
            except ValueError as exc:
                return _err(400, str(exc))
        user_id, email = _user(request)
        if user_id:
            try:
                store.ensure_user(user_id, email)
            except StoreError:
                pass    # the job still runs; the mirror row is optional
        job = server.submit(payload, user_id=user_id)
        if not job:
            return _err(400, "provide a question or a topic")
        return JSONResponse({"id": job.id, "job": job.public()},
                            status_code=202)

    @app.post("/api/run")
    async def run_job(request: Request) -> Response:
        return _start_job(await _json_body(request), request)

    @app.post("/api/generate")
    async def generate_job(request: Request) -> Response:
        return _start_job(await _json_body(request), request)

    @app.get("/api/jobs")
    def jobs() -> Response:
        return _safe(lambda: JSONResponse({"jobs": server.list_jobs()}))

    @app.get("/api/jobs/{job_id}")
    def job_detail(job_id: str) -> Response:
        record = server.get_job(job_id)
        if not record:
            return _err(404, "no such job")
        return JSONResponse(record.public())

    @app.get("/api/lectures")
    def lectures() -> Response:
        return _safe(lambda: JSONResponse(
            {"lectures": sorted(server.list_lectures(),
                                key=lambda lec: -lec["modified"])}))

    @app.delete("/api/lectures/{slug}")
    def lecture_delete(slug: str) -> Response:
        if server.delete_lecture(slug):
            return JSONResponse({"deleted": slug})
        return _err(404, "no such lecture")

    @app.get("/api/lectures/{slug}/video")
    def lecture_video(slug: str, request: Request) -> Response:
        video = server.resolve_video(slug)
        if video is not None:
            return _file_response(video, request, video=True)
        # cloud mode: the permanent copy lives on Cloudinary
        try:
            for lec in server.list_lectures():
                if lec["slug"] == slug and str(
                        lec.get("video") or "").startswith("http"):
                    return RedirectResponse(lec["video"], status_code=307)
        except StoreError:
            pass
        return _err(404, "no such lecture")

    # ------------------------------------------------------------- chats

    @app.get("/api/chats")
    def chats() -> Response:
        return _safe(lambda: JSONResponse({"chats": server.list_chats()}))

    @app.get("/api/chats/{chat_id}")
    def chat_detail(chat_id: str) -> Response:
        chat = server.load_chat_by_id(chat_id)
        if not chat:
            return _err(404, "no such chat")
        return JSONResponse(chat)

    @app.post("/api/chats/{chat_id}")
    async def chat_save(chat_id: str, request: Request) -> Response:
        payload = await _json_body(request)
        if server.save_chat_by_id(chat_id, payload):
            return JSONResponse({"ok": True, "id": chat_id})
        return _err(400, "invalid chat")

    @app.delete("/api/chats/{chat_id}")
    def chat_delete(chat_id: str) -> Response:
        if server.delete_chat_by_id(chat_id):
            return JSONResponse({"ok": True})
        return _err(404, "no such chat")

    # ------------------------------------------------ misc app endpoints

    @app.get("/api/config")
    def config() -> dict:
        topics, llm_configured = server.topics()
        return {"llm_configured": llm_configured,
                "topics": topics,
                "themes": ["auto", "math", "lab", "spatial", "data",
                           "paper"],
                "voices": ["en-US-AriaNeural", "en-US-GuyNeural",
                           "en-GB-SoniaNeural", "hi-IN-SwaraNeural"],
                "qualities": ["l", "m", "h"],
                "tts_engines": ["edge", "gtts", "silence"],
                "transitions": ["none", "flip"]}

    @app.get("/api/search")
    def search(q: str = "") -> dict:
        return {"lectures": server.search(q), "query": q}

    @app.get("/api/status")
    def status() -> dict:
        return server.status()

    # ----------------------------------------------------- static (local)

    @app.get("/{path:path}")
    def static_files(path: str) -> Response:
        target = server.resolve_static(f"/{path}")
        if target is None:
            if "." in path.rsplit("/", 1)[-1] or path.startswith("api/"):
                return _err(404, "not found")
            target = server.resolve_static("/index.html")
            if target is None:
                return _err(404, "not found")
        return FileResponse(target)

    # -------------------------------------------------------- file sender

    def _file_response(target: Path, request: Request,
                       video: bool = False) -> Response:
        """Serve a file with HTTP Range support (seekable video player)."""
        import re as _re
        total = target.stat().st_size
        ctype = ("video/mp4" if video else
                 ("application/octet-stream" if target.suffix == ".mp4"
                  else "text/plain"))
        header = request.headers.get("Range") if video else None
        match = _re.match(r"bytes=(\d*)-(\d*)$", header) if header else None
        first, last = (match.groups() if match else ("", ""))
        if first:
            start = int(first)
            end = min(int(last), total - 1) if last else total - 1
        elif last:
            start = max(total - int(last), 0)
            end = total - 1
        else:
            start, end = 0, total - 1
        if start > end or start >= total:
            return Response(status_code=416, headers={
                "Content-Range": f"bytes */{total}"})
        length = end - start + 1
        with target.open("rb") as handle:
            handle.seek(start)
            body = handle.read(length)
        headers = {"Accept-Ranges": "bytes",
                   "Cache-Control": "no-store"}
        if header:
            headers["Content-Range"] = f"bytes {start}-{end}/{total}"
        return Response(body, status_code=206 if header else 200,
                        media_type=ctype, headers=headers)

    app.state.server = server
    return app


async def _json_body(request: Request) -> dict:
    raw = await request.body()
    if len(raw) > 1_000_000:
        return {}
    try:
        data = json.loads(raw or b"{}")
        return data if isinstance(data, dict) else {}
    except ValueError:
        return {}


def __getattr__(name):
    """`uvicorn phiversity.api:app` builds the app lazily on first use,
    so importing this module never touches disks or services."""
    if name == "app":
        globals()["app"] = create_app()
        return globals()["app"]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="phiversity-api",
        description="Serve the Phiversity cloud API (FastAPI).")
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int,
                        default=int(os.environ.get("PORT", "8787")))
    parser.add_argument("--root", default=None, metavar="DIR")
    args = parser.parse_args(argv)
    import uvicorn
    uvicorn.run(create_app(args.root), host=args.host, port=args.port,
                log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
