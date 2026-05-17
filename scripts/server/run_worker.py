import argparse
import os
import socket
import time

from dotenv import load_dotenv

from scripts.server.database import SessionLocal
from scripts.server.logger import logger
from scripts.server.services.job_service import JobService, _worker_poll_interval_seconds


def _default_worker_id() -> str:
    configured = (os.getenv("WORKER_ID") or "").strip()
    if configured:
        return configured
    return f"worker-{socket.gethostname()}-{os.getpid()}"


def _process_one_job(worker_id: str) -> bool:
    with SessionLocal() as db:
        service = JobService(db)
        claimed = service.claim_next_job(worker_id)
        if not claimed:
            return False
        job_id = claimed.id

    with SessionLocal() as db:
        JobService(db).run_claimed_job(job_id)
    return True


def main() -> int:
    load_dotenv(override=True)

    parser = argparse.ArgumentParser(description="Run the Phiversity background worker")
    parser.add_argument("--once", action="store_true", help="Claim and process at most one job")
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=None,
        help="Seconds to wait between queue polls in loop mode",
    )
    args = parser.parse_args()

    worker_id = _default_worker_id()
    poll_interval = args.poll_interval if args.poll_interval is not None else _worker_poll_interval_seconds()

    logger.info(
        "Starting background worker",
        extra={"worker_id": worker_id, "poll_interval": poll_interval},
    )

    while True:
        processed = _process_one_job(worker_id)
        if args.once:
            return 0
        if not processed:
            time.sleep(poll_interval)


if __name__ == "__main__":
    raise SystemExit(main())
