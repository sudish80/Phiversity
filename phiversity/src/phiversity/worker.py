"""Standalone render worker for Phiversity.

The FastAPI service accepts jobs; this process does the heavy lifting
(plan -> TTS -> Manim -> ffmpeg). It polls the storage queue, claims one
queued job at a time and runs the same pipeline the local server runs.
Keep it in sync with the API service: both must be deployed from the
same commit and share the same store + LLM/TTS configuration.

Deploy it wherever a long render is allowed to run (Render Background
Worker, Railway worker, any VPS with cron/systemd):

    phiversity-worker --poll 5

Requires SUPABASE_URL + SUPABASE_SERVICE_KEY (the shared queue), plus
LLM_API_KEY, CLOUDINARY_* for the same behaviour as the web service.
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from .config import load_env_file
from .server import Job, RenderServer
from .store import open_store


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="phiversity-worker",
        description="Standalone Phiversity render worker (queue -> "
                    "pipeline).")
    parser.add_argument("--poll", type=float,
                        default=float(os.environ.get(
                            "PHIVERSITY_WORKER_POLL", "5")),
                        help="seconds between queue polls (default 5)")
    parser.add_argument("--root", default=None, metavar="DIR",
                        help="workspace root (default: PHIVERSITY_ROOT "
                             "or the current directory)")
    args = parser.parse_args(argv)

    load_env_file()
    root = Path(args.root or os.environ.get("PHIVERSITY_ROOT") or ".").resolve()
    frontend = root / "Frontend"          # not served here; path only
    lectures = (Path(os.environ["PHIVERSITY_OUT_DIR"]).resolve()
                if os.environ.get("PHIVERSITY_OUT_DIR")
                else root / "lectures")
    lectures.mkdir(parents=True, exist_ok=True)

    store = open_store(root)
    if not hasattr(store, "claim_next_queued"):
        print("[worker] this storage backend has no queue; set "
              "SUPABASE_URL + SUPABASE_SERVICE_KEY")
        return 2

    server = RenderServer(frontend, lectures, store=store,
                          inline_worker=False)
    kind = getattr(store, "kind", "?")
    print(f"[worker] polling {kind} queue every {args.poll:g}s "
          f"(Ctrl-C to stop)")
    while True:
        try:
            record = store.claim_next_queued()
        except KeyboardInterrupt:
            print("\n[worker] stopped")
            return 0
        except Exception as exc:  # noqa: BLE001 - keep polling
            print(f"[worker] store error: {exc}")
            time.sleep(args.poll)
            continue
        if not record:
            time.sleep(args.poll)
            continue
        job = Job.from_record(record)
        job.persist = lambda j=job: store.save_job(j.to_record())
        with server.lock:
            server.jobs[job.id] = job
        print(f"[worker] running job {job.id}: "
              f"{job.question or job.topic!r}")
        try:
            server._run_job(job, job.payload or {})
        except Exception as exc:  # noqa: BLE001 - never die on a job
            job.status = "error"
            job.error = str(exc)
            job.log(f"[error] worker crashed: {exc}")
            try:
                job.persist()
            except Exception:  # noqa: BLE001
                print(f"[worker] could not persist the failure: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
