import json
import os
import socket
import subprocess
import sys
import threading
import time
import uuid
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from .base import BaseService
from .notification_service import NotificationService
from .job_error_taxonomy import (
    JOB_EXIT_ARTIFACT_ERROR,
    JOB_EXIT_SUCCESS,
    JOB_EXIT_TIMEOUT,
    JOB_EXIT_VALIDATION_ERROR,
    JOB_EXIT_WORKFLOW_ERROR,
    STAGE_ARTIFACT,
    STAGE_ORCHESTRATION,
    STAGE_PIPELINE,
    STAGE_QUEUE,
    STAGE_VALIDATION,
    STAGE_WORKFLOW,
    infer_root_cause_hint,
)
from ..models import JobModel

try:
    from scripts.cloud_storage import storage as cloud_storage
except Exception:
    cloud_storage = None

_LOG_FLUSH_INTERVAL = 5
_JOB_SLOT_CONDITION = threading.Condition()
_ACTIVE_JOB_COUNT = 0


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _format_utc_timestamp() -> str:
    return _utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _job_timeout_seconds() -> int:
    try:
        return max(int(os.getenv("JOB_TIMEOUT", "1200")), 60)
    except ValueError:
        return 1200


def _job_lease_seconds() -> int:
    return _job_timeout_seconds() + 60


def _max_concurrent_jobs() -> int:
    try:
        return max(int(os.getenv("MAX_CONCURRENT_JOBS", "1")), 1)
    except ValueError:
        return 1


def _worker_poll_interval_seconds() -> float:
    try:
        return max(float(os.getenv("WORKER_POLL_INTERVAL_SECONDS", "2")), 0.25)
    except ValueError:
        return 2.0


def _job_execution_mode() -> str:
    configured = (os.getenv("JOB_EXECUTION_MODE") or "").strip().lower()
    if configured in {"inline", "worker"}:
        return configured

    env_name = (
        os.getenv("PHIVERSITY_ENV")
        or os.getenv("APP_ENV")
        or os.getenv("ENVIRONMENT")
        or ""
    ).strip().lower()
    return "worker" if env_name in {"prod", "production", "staging"} else "inline"


def _acquire_job_slot(timeout_seconds: int) -> bool:
    global _ACTIVE_JOB_COUNT

    deadline = time.monotonic() + max(timeout_seconds, 1)
    with _JOB_SLOT_CONDITION:
        while _ACTIVE_JOB_COUNT >= _max_concurrent_jobs():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            _JOB_SLOT_CONDITION.wait(timeout=remaining)
        _ACTIVE_JOB_COUNT += 1
        return True


def _release_job_slot() -> None:
    global _ACTIVE_JOB_COUNT

    with _JOB_SLOT_CONDITION:
        if _ACTIVE_JOB_COUNT > 0:
            _ACTIVE_JOB_COUNT -= 1
        _JOB_SLOT_CONDITION.notify()


class JobService(BaseService):
    _ALERT_LOCK = threading.Lock()
    _LAST_ALERT_BY_STAGE: dict[str, float] = {}

    def _log_event(self, db_job: JobModel, message: str, level: str = "INFO", stage: str = "workflow", db: Session = None) -> None:
        clean = (message or "").rstrip("\n")
        correlation_id = f"job:{db_job.id}"
        entry = f"{_format_utc_timestamp()} | {level.upper():<5} | {stage:<12} | cid={correlation_id} | {clean}\n"
        self._append_log(db_job, entry, db=db)

    def _format_command_output_line(self, db_job: JobModel, line: str) -> str:
        clean = (line or "").rstrip("\n")
        return f"{_format_utc_timestamp()} | CMD   | process      | cid=job:{db_job.id} | {clean}\n"

    def _db_log_max_chars(self) -> int:
        try:
            return max(int(os.getenv("DB_LOG_MAX_CHARS", "200000")), 5000)
        except ValueError:
            return 200000

    def _file_log_rotation_max_bytes(self) -> int:
        try:
            return max(int(os.getenv("JOB_LOG_FILE_MAX_BYTES", "5242880")), 1048576)
        except ValueError:
            return 5242880

    def _file_log_rotation_backups(self) -> int:
        try:
            return max(int(os.getenv("JOB_LOG_FILE_BACKUPS", "3")), 1)
        except ValueError:
            return 3

    def _alert_threshold(self) -> int:
        try:
            return max(int(os.getenv("JOB_FAILURE_ALERT_THRESHOLD", "3")), 1)
        except ValueError:
            return 3

    def _alert_window_minutes(self) -> int:
        try:
            return max(int(os.getenv("JOB_FAILURE_ALERT_WINDOW_MINUTES", "15")), 1)
        except ValueError:
            return 15

    def _alert_cooldown_seconds(self) -> int:
        try:
            return max(int(os.getenv("JOB_FAILURE_ALERT_COOLDOWN_SECONDS", "900")), 60)
        except ValueError:
            return 900

    def _rotate_log_file_if_needed(self, log_path: Path, incoming_text: str) -> None:
        max_bytes = self._file_log_rotation_max_bytes()
        backups = self._file_log_rotation_backups()
        incoming_bytes = len((incoming_text or "").encode("utf-8", errors="ignore"))

        try:
            current_size = log_path.stat().st_size if log_path.exists() else 0
        except Exception:
            current_size = 0

        if current_size + incoming_bytes <= max_bytes:
            return

        oldest_backup = log_path.with_name(f"{log_path.name}.{backups}")
        if oldest_backup.exists():
            oldest_backup.unlink(missing_ok=True)

        for idx in range(backups - 1, 0, -1):
            src = log_path.with_name(f"{log_path.name}.{idx}")
            dst = log_path.with_name(f"{log_path.name}.{idx + 1}")
            if src.exists():
                src.replace(dst)

        if log_path.exists():
            log_path.replace(log_path.with_name(f"{log_path.name}.1"))

    def _maybe_send_failure_alert(self, stage: str, recent_failures: int, hint: str) -> None:
        webhook = (os.getenv("JOB_FAILURE_ALERT_WEBHOOK_URL") or "").strip()
        email_to = (os.getenv("JOB_FAILURE_ALERT_EMAIL") or "").strip()

        if not webhook and not email_to:
            return

        payload = {
            "event": "job_failure_threshold_exceeded",
            "stage": stage,
            "recent_failures": recent_failures,
            "window_minutes": self._alert_window_minutes(),
            "hint": hint,
            "timestamp": _format_utc_timestamp(),
        }

        if webhook:
            try:
                requests.post(webhook, json=payload, timeout=5)
            except Exception as exc:
                self.logger.warning(f"Alert webhook failed: {exc}")

        if email_to:
            try:
                NotificationService().send_email(
                    email_to,
                    subject=f"Phiversity alert: repeated {stage} failures",
                    body=json.dumps(payload, indent=2),
                )
            except Exception as exc:
                self.logger.warning(f"Alert email failed: {exc}")

    def _maybe_alert_repeated_stage_failures(self, stage: str, hint: str) -> None:
        threshold = self._alert_threshold()
        window = timedelta(minutes=self._alert_window_minutes())
        cutoff = _utcnow() - window

        recent_failures = (
            self.db.query(func.count(JobModel.id))
            .filter(
                JobModel.status == "error",
                JobModel.finished_at.is_not(None),
                JobModel.finished_at >= cutoff,
                JobModel.log.is_not(None),
                JobModel.log.like(f"%failed_stage: {stage}%"),
            )
            .scalar()
            or 0
        )

        if recent_failures < threshold:
            return

        now = time.monotonic()
        cooldown = self._alert_cooldown_seconds()
        with self._ALERT_LOCK:
            last_sent = self._LAST_ALERT_BY_STAGE.get(stage, 0.0)
            if now - last_sent < cooldown:
                return
            self._LAST_ALERT_BY_STAGE[stage] = now

        self._maybe_send_failure_alert(stage, recent_failures, hint)

    def cleanup_old_artifact_logs(self) -> dict:
        root = Path(__file__).resolve().parents[3]
        log_root = root / "media" / "videos" / "web_jobs"
        retention_days = max(int(os.getenv("JOB_LOG_RETENTION_DAYS", "14")), 1)
        cutoff_ts = (_utcnow() - timedelta(days=retention_days)).timestamp()
        deleted_files = 0

        if log_root.exists():
            for path in log_root.rglob("log.txt*"):
                try:
                    if path.is_file() and path.stat().st_mtime < cutoff_ts:
                        path.unlink()
                        deleted_files += 1
                except Exception:
                    continue

        stale_cutoff = _utcnow() - timedelta(days=retention_days)
        keep_chars = max(int(os.getenv("DB_LOG_RETENTION_CHARS", "4000")), 500)
        truncated_rows = 0
        stale_jobs = (
            self.db.query(JobModel)
            .filter(JobModel.finished_at.is_not(None), JobModel.finished_at < stale_cutoff)
            .all()
        )
        for row in stale_jobs:
            if row.log and len(row.log) > keep_chars:
                row.log = "...[archived older log content]...\n" + row.log[-keep_chars:]
                truncated_rows += 1

        if truncated_rows:
            self.db.commit()

        return {"deleted_log_files": deleted_files, "truncated_db_logs": truncated_rows}

    def _job_duration_seconds(self, db_job: JobModel, finished_at: Optional[datetime] = None) -> int:
        end_time = finished_at or _utcnow()
        start_time = db_job.started_at or db_job.claimed_at or db_job.created_at
        if not start_time:
            return 0

        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)

        return max(int((end_time - start_time).total_seconds()), 0)

    def _append_job_summary(
        self,
        db_job: JobModel,
        *,
        status: str,
        failed_stage: str,
        exit_code: int,
        total_duration_seconds: int,
        next_action_hint: str,
        stage_durations_seconds: Optional[dict] = None,
        db: Session = None,
    ) -> None:
        stage_durations_seconds = stage_durations_seconds or {}
        lines = [
            "\n=== JOB SUMMARY ===\n",
            f"status: {status}\n",
            f"failed_stage: {failed_stage}\n",
            f"exit_code: {exit_code}\n",
            f"total_duration_seconds: {total_duration_seconds}\n",
            f"stage_durations_seconds: {json.dumps(stage_durations_seconds, sort_keys=True)}\n",
            f"next_action_hint: {next_action_hint}\n",
            "===================\n",
        ]
        self._append_log(db_job, "".join(lines), db=db)

    def extract_job_summary(self, db_job: JobModel) -> Optional[dict]:
        content = db_job.log or ""
        marker = "=== JOB SUMMARY ==="
        idx = content.rfind(marker)
        if idx < 0:
            return None

        block = content[idx:].splitlines()
        values: dict[str, str] = {}
        for line in block:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()

        if "status" not in values:
            return None

        stage_durations = {}
        raw_stage_durations = values.get("stage_durations_seconds", "{}")
        try:
            parsed = json.loads(raw_stage_durations)
            if isinstance(parsed, dict):
                stage_durations = {str(k): int(v) for k, v in parsed.items()}
        except Exception:
            stage_durations = {}

        return {
            "status": values.get("status", db_job.status),
            "failed_stage": values.get("failed_stage", "none"),
            "exit_code": int(values.get("exit_code", "0") or 0),
            "total_duration_seconds": int(values.get("total_duration_seconds", "0") or 0),
            "stage_durations_seconds": stage_durations,
            "next_action_hint": values.get("next_action_hint", "No action required."),
        }

    def create_job(self) -> JobModel:
        job = JobModel(id=str(uuid.uuid4()))
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job(self, job_id: str) -> Optional[JobModel]:
        return self.db.query(JobModel).filter(JobModel.id == job_id).first()

    def start_background_job(self, job_id: str, req_data: dict):
        db_job = self.get_job(job_id)
        if not db_job:
            return

        self._store_request_payload(db_job, req_data)
        mode = _job_execution_mode()
        self._log_event(db_job, f"[server] Job queued in {mode} execution mode", stage="queue")

        if mode == "inline":
            thread = threading.Thread(target=self._run_inline_job, args=(job_id,))
            thread.daemon = True
            thread.start()

    def _store_request_payload(self, db_job: JobModel, req_data: dict) -> None:
        db_job.request_payload = json.dumps(req_data, sort_keys=True)
        db_job.status = "queued"
        db_job.progress = 0
        db_job.video_path = None
        db_job.video_url = None
        db_job.worker_id = None
        db_job.claimed_at = None
        db_job.started_at = None
        db_job.finished_at = None
        db_job.lease_expires_at = None
        self.db.commit()

    def _run_inline_job(self, job_id: str) -> None:
        from dotenv import load_dotenv
        from scripts.server.database import SessionLocal

        load_dotenv(override=True)
        worker_id = f"inline-{socket.gethostname()}-{os.getpid()}-{threading.get_ident()}"

        db = SessionLocal()
        try:
            service = JobService(db)
            if service.claim_job(job_id, worker_id):
                service.run_claimed_job(job_id, acquire_local_slot=True)
        finally:
            db.close()

    def recover_interrupted_jobs(self, reason: str = "worker restart") -> int:
        now = _utcnow()
        stale_jobs = (
            self.db.query(JobModel)
            .filter(
                JobModel.status == "running",
                or_(
                    JobModel.lease_expires_at.is_(None),
                    JobModel.lease_expires_at <= now,
                ),
            )
            .all()
        )

        recovered = 0
        for db_job in stale_jobs:
            if db_job.request_payload:
                db_job.status = "queued"
                db_job.progress = min(db_job.progress or 0, 5)
                db_job.worker_id = None
                db_job.claimed_at = None
                db_job.started_at = None
                db_job.finished_at = None
                db_job.lease_expires_at = None
                db_job.log = (
                    (db_job.log or "")
                    + f"\n[server] Job re-queued after {reason}.\n"
                )
            else:
                db_job.status = "error"
                db_job.finished_at = now
                db_job.lease_expires_at = None
                db_job.log = (
                    (db_job.log or "")
                    + f"\n[server] Job could not be recovered after {reason}: missing payload.\n"
                )
            recovered += 1

        if recovered:
            self.db.commit()
        return recovered

    def claim_job(self, job_id: str, worker_id: str) -> Optional[JobModel]:
        candidate = self.get_job(job_id)
        if not candidate or candidate.status != "queued":
            return None

        now = _utcnow()
        attempts = (candidate.attempt_count or 0) + 1
        claimed = (
            self.db.query(JobModel)
            .filter(JobModel.id == job_id, JobModel.status == "queued")
            .update(
                {
                    JobModel.status: "running",
                    JobModel.progress: max(candidate.progress or 0, 5),
                    JobModel.worker_id: worker_id,
                    JobModel.claimed_at: now,
                    JobModel.started_at: now,
                    JobModel.finished_at: None,
                    JobModel.lease_expires_at: now + timedelta(seconds=_job_lease_seconds()),
                    JobModel.attempt_count: attempts,
                },
                synchronize_session=False,
            )
        )
        if not claimed:
            self.db.rollback()
            return None

        self.db.commit()
        db_job = self.get_job(job_id)
        if db_job:
            self._log_event(db_job, f"[server] Job claimed by worker {worker_id}", stage="queue")
        return db_job

    def claim_next_job(self, worker_id: str) -> Optional[JobModel]:
        self.recover_interrupted_jobs(reason="expired worker lease")
        candidate_ids = [
            job_id
            for (job_id,) in self.db.query(JobModel.id)
            .filter(JobModel.status == "queued")
            .order_by(JobModel.created_at.asc())
            .limit(25)
            .all()
        ]

        for job_id in candidate_ids:
            claimed = self.claim_job(job_id, worker_id)
            if claimed:
                return claimed
        return None

    def queue_metrics(self) -> dict:
        now = _utcnow()
        queued_count = self.db.query(func.count(JobModel.id)).filter(JobModel.status == "queued").scalar() or 0
        running_count = self.db.query(func.count(JobModel.id)).filter(JobModel.status == "running").scalar() or 0
        error_count = self.db.query(func.count(JobModel.id)).filter(JobModel.status == "error").scalar() or 0
        stale_lease_count = (
            self.db.query(func.count(JobModel.id))
            .filter(
                JobModel.status == "running",
                JobModel.lease_expires_at.is_not(None),
                JobModel.lease_expires_at <= now,
            )
            .scalar()
            or 0
        )
        oldest_queued = (
            self.db.query(JobModel)
            .filter(JobModel.status == "queued")
            .order_by(JobModel.created_at.asc())
            .first()
        )
        latest_finished = self.db.query(func.max(JobModel.finished_at)).scalar()

        oldest_queued_age_seconds = None
        if oldest_queued and oldest_queued.created_at:
            created_at = oldest_queued.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            oldest_queued_age_seconds = max(int((now - created_at).total_seconds()), 0)

        return {
            "job_execution_mode": _job_execution_mode(),
            "max_concurrent_jobs": _max_concurrent_jobs(),
            "queued_jobs": queued_count,
            "running_jobs": running_count,
            "error_jobs": error_count,
            "stale_leased_jobs": stale_lease_count,
            "oldest_queued_job_age_seconds": oldest_queued_age_seconds,
            "latest_finished_at": latest_finished.isoformat() if latest_finished else None,
        }

    def _append_log(self, db_job: JobModel, text: str, db: Session = None):
        db_session = db or self.db
        next_log = (db_job.log or "") + text
        max_chars = self._db_log_max_chars()
        if len(next_log) > max_chars:
            truncated = len(next_log) - max_chars
            next_log = f"...[truncated {truncated} chars]...\n" + next_log[-max_chars:]
        db_job.log = next_log
        db_session.commit()
        if db_job.out_dir:
            try:
                log_path = Path(db_job.out_dir) / "log.txt"
                self._rotate_log_file_if_needed(log_path, text)
                with open(log_path, "a", encoding="utf-8", errors="ignore") as f:
                    f.write(text)
            except Exception as e:
                self.logger.error(f"Failed to write to log file: {e}")

    def _flush_log_buffer(self, db_job: JobModel, buf: List[str], db: Session = None):
        if not buf:
            return
        self._append_log(db_job, "".join(buf), db=db)
        buf.clear()

    def _run_and_capture(
        self,
        cmd: List[str],
        cwd: Path,
        db_job: JobModel,
        db: Session = None,
        timeout_seconds: Optional[int] = None,
        stage: str = STAGE_WORKFLOW,
    ) -> int:
        self._log_event(db_job, "Starting command execution", stage="process", db=db)
        self._append_log(db_job, f"\n$ {' '.join(cmd)}\n", db=db)
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            stream = proc.stdout
            assert stream is not None
            timed_out = False
            killer = None

            if timeout_seconds is not None:

                def _kill_process():
                    nonlocal timed_out
                    if proc.poll() is None:
                        timed_out = True
                        try:
                            proc.kill()
                        except Exception:
                            pass

                killer = threading.Timer(max(timeout_seconds, 1), _kill_process)
                killer.daemon = True
                killer.start()

            buf: List[str] = []
            recent_raw_lines: List[str] = []
            line_count = 0
            try:
                for line in stream:
                    buf.append(self._format_command_output_line(db_job, line))
                    recent_raw_lines.append(line.rstrip("\n"))
                    if len(recent_raw_lines) > 80:
                        recent_raw_lines = recent_raw_lines[-80:]
                    line_count += 1
                    if "[pipeline]" in line:
                        if "Step 1" in line:
                            db_job.progress = 42
                        elif "Step 2" in line:
                            db_job.progress = 50
                        elif "Step 3" in line:
                            db_job.progress = 60
                        elif "Step 4" in line:
                            db_job.progress = 70
                        elif "Step 5" in line:
                            db_job.progress = 85
                        self._flush_log_buffer(db_job, buf, db=db)
                    elif line_count % _LOG_FLUSH_INTERVAL == 0:
                        self._flush_log_buffer(db_job, buf, db=db)
            finally:
                if killer is not None:
                    killer.cancel()
                stream.close()

            self._flush_log_buffer(db_job, buf, db=db)
            rc = proc.wait()
            if timed_out:
                self._log_event(
                    db_job,
                    f"[server] Command timed out after {timeout_seconds}s and was terminated",
                    level="ERROR",
                    stage="process",
                    db=db,
                )
                return 124
            if rc != 0:
                hint = infer_root_cause_hint(stage, "\n".join(recent_raw_lines), rc)
                self._log_event(
                    db_job,
                    f"[server] Command exited with non-zero status {rc}. hint={hint}",
                    level="ERROR",
                    stage="process",
                    db=db,
                )
            else:
                self._log_event(db_job, "Command completed successfully", stage="process", db=db)
            return rc
        except Exception as e:
            self._log_event(db_job, f"Exception: {e}", level="ERROR", stage="process", db=db)
            return 1

    def _persist_completed_artifacts(self, db_job: JobModel, out_dir: Path, plan_path: Path):
        final_video = out_dir / "final.mp4"
        log_path = out_dir / "log.txt"

        cloud_enabled = (
            cloud_storage is not None
            and getattr(cloud_storage, "backend", "local") != "local"
        )

        if final_video.exists():
            video_ref = str(final_video)
            if cloud_enabled:
                try:
                    video_ref = cloud_storage.upload_video(final_video, db_job.id)
                except Exception as e:
                    self._append_log(
                        db_job,
                        f"[server] Cloud video upload failed, using local artifact: {e}\n",
                    )
            db_job.video_path = video_ref
            db_job.video_url = f"/api/v1/jobs/{db_job.id}/video"
        else:
            db_job.video_path = None
            db_job.video_url = None

        if plan_path.exists():
            plan_ref = str(plan_path)
            if cloud_enabled:
                try:
                    plan_ref = cloud_storage.upload_json(plan_path, db_job.id)
                except Exception as e:
                    self._append_log(
                        db_job,
                        f"[server] Cloud plan upload failed, using local artifact: {e}\n",
                    )
            db_job.plan_path = plan_ref
            db_job.plan_url = f"/api/v1/jobs/{db_job.id}/plan"

        if log_path.exists():
            db_job.log_path = str(log_path)
            db_job.log_url = f"/api/v1/jobs/{db_job.id}/log"
        else:
            db_job.log_path = None
            db_job.log_url = None

    def _remaining_timeout(self, deadline: float) -> int:
        remaining = int(deadline - time.monotonic())
        return max(remaining, 0)

    def _load_request_payload(self, db_job: JobModel) -> Optional[dict]:
        if not db_job.request_payload:
            return None
        try:
            payload = json.loads(db_job.request_payload)
        except json.JSONDecodeError:
            return None
        if isinstance(payload, dict):
            return payload
        return None

    def _mark_job_error(
        self,
        db_job: JobModel,
        message: str,
        db: Session = None,
        *,
        stage: str = STAGE_WORKFLOW,
        exit_code: int = JOB_EXIT_WORKFLOW_ERROR,
        next_action_hint: str = "Inspect the command output and retry the job.",
        stage_durations_seconds: Optional[dict] = None,
    ) -> None:
        db_session = db or self.db
        self._log_event(db_job, message, level="ERROR", stage=stage, db=db_session)
        db_job.status = "error"
        db_job.finished_at = _utcnow()
        db_job.lease_expires_at = None
        db_session.commit()
        self._append_job_summary(
            db_job,
            status="error",
            failed_stage=stage,
            exit_code=exit_code,
            total_duration_seconds=self._job_duration_seconds(db_job, db_job.finished_at),
            next_action_hint=next_action_hint,
            stage_durations_seconds=stage_durations_seconds,
            db=db_session,
        )
        self._maybe_alert_repeated_stage_failures(stage, next_action_hint)

    def run_claimed_job(self, job_id: str, acquire_local_slot: bool = False) -> None:
        from dotenv import load_dotenv

        db_job = self.get_job(job_id)
        if not db_job:
            return

        req_data = self._load_request_payload(db_job)
        if not req_data:
            self._mark_job_error(
                db_job,
                "[server] Missing or invalid job payload\n",
                stage=STAGE_VALIDATION,
                exit_code=JOB_EXIT_VALIDATION_ERROR,
                next_action_hint="Verify request payload JSON and required fields before queueing.",
            )
            return

        load_dotenv(override=True)
        slot_acquired = False
        stage_durations_seconds: dict[str, int] = {}
        try:
            job_timeout = _job_timeout_seconds()
            deadline = time.monotonic() + job_timeout

            if acquire_local_slot:
                self._log_event(
                    db_job,
                    f"[server] Waiting for execution slot (max {_max_concurrent_jobs()} concurrent jobs, timeout {job_timeout}s)",
                    stage="queue",
                )
                if not _acquire_job_slot(job_timeout):
                    self._mark_job_error(
                        db_job,
                        "[server] Timed out waiting for an execution slot\n",
                        stage=STAGE_QUEUE,
                        exit_code=JOB_EXIT_TIMEOUT,
                        next_action_hint="Increase MAX_CONCURRENT_JOBS or reduce active queue load.",
                        stage_durations_seconds=stage_durations_seconds,
                    )
                    return
                slot_acquired = True

            root = Path(__file__).resolve().parents[3]
            out_dir = root / "media" / "videos" / "web_jobs" / db_job.id
            out_dir.mkdir(parents=True, exist_ok=True)
            stale_video = out_dir / "final.mp4"
            if stale_video.exists():
                stale_video.unlink()
            db_job.out_dir = str(out_dir)
            db_job.video_path = None
            db_job.video_url = None

            python = sys.executable
            plan_path = root / "media" / "texts" / f"solution_plan_{db_job.id}.json"
            db_job.plan_path = str(plan_path)
            db_job.finished_at = None
            self.db.commit()

            if req_data.get("orchestrate"):
                db_job.progress = 10
                self.db.commit()
                cmd_1 = [
                    python,
                    "-m",
                    "scripts.orchestrator.run_orchestrator",
                    req_data["problem"],
                    "--out",
                    str(plan_path),
                ]
                mode = req_data.get("mode") or "question_solving"
                cmd_1.extend(["--mode", str(mode)])
                if req_data.get("long_video"):
                    cmd_1.append("--long-video")
                if req_data.get("custom_prompt"):
                    cmd_1.extend(["--prompt", req_data["custom_prompt"]])

                self._log_event(db_job, "[server] Starting LLM orchestration...", stage="orchestration")
                orchestration_started = time.monotonic()
                remaining = self._remaining_timeout(deadline)
                if remaining <= 0:
                    self._mark_job_error(
                        db_job,
                        "[server] Job timed out before orchestration started\n",
                        stage=STAGE_ORCHESTRATION,
                        exit_code=JOB_EXIT_TIMEOUT,
                        next_action_hint="Increase JOB_TIMEOUT or reduce orchestration complexity.",
                        stage_durations_seconds=stage_durations_seconds,
                    )
                    return

                rc1 = self._run_and_capture(
                    cmd_1,
                    root,
                    db_job,
                    timeout_seconds=remaining,
                    stage=STAGE_ORCHESTRATION,
                )
                stage_durations_seconds[STAGE_ORCHESTRATION] = max(int(time.monotonic() - orchestration_started), 0)
                if rc1 != 0:
                    failure_line = (
                        "[server] LLM orchestration timed out\n"
                        if rc1 == 124
                        else "[server] LLM orchestration failed\n"
                    )
                    hint = infer_root_cause_hint(STAGE_ORCHESTRATION, db_job.log, rc1)
                    self._mark_job_error(
                        db_job,
                        failure_line,
                        stage=STAGE_ORCHESTRATION,
                        exit_code=rc1,
                        next_action_hint=hint,
                        stage_durations_seconds=stage_durations_seconds,
                    )
                    return
                db_job.progress = 30
                self.db.commit()
                self._log_event(db_job, "[server] LLM orchestration finished", stage="orchestration")

            cmd_2 = [python, "-m", "scripts.pipeline", "--json", str(plan_path), "--out-dir", str(out_dir)]
            if req_data.get("voice_first"):
                cmd_2.append("--voice-first")
            if req_data.get("element_audio"):
                cmd_2.append("--element-audio")

            self._log_event(db_job, "[server] Starting pipeline rendering...", stage="pipeline")
            pipeline_started = time.monotonic()
            remaining = self._remaining_timeout(deadline)
            if remaining <= 0:
                self._mark_job_error(
                    db_job,
                    "[server] Job timed out before pipeline rendering started\n",
                    stage=STAGE_PIPELINE,
                    exit_code=JOB_EXIT_TIMEOUT,
                    next_action_hint="Increase JOB_TIMEOUT or reduce rendering complexity.",
                    stage_durations_seconds=stage_durations_seconds,
                )
                return

            rc2 = self._run_and_capture(
                cmd_2,
                root,
                db_job,
                timeout_seconds=remaining,
                stage=STAGE_PIPELINE,
            )
            stage_durations_seconds[STAGE_PIPELINE] = max(int(time.monotonic() - pipeline_started), 0)
            if rc2 != 0:
                failure_line = "[server] Pipeline timed out\n" if rc2 == 124 else "[server] Pipeline failed\n"
                hint = infer_root_cause_hint(STAGE_PIPELINE, db_job.log, rc2)
                self._mark_job_error(
                    db_job,
                    failure_line,
                    stage=STAGE_PIPELINE,
                    exit_code=rc2,
                    next_action_hint=hint,
                    stage_durations_seconds=stage_durations_seconds,
                )
                return

            self._persist_completed_artifacts(db_job, out_dir, plan_path)
            if not db_job.video_path:
                self._mark_job_error(
                    db_job,
                    "[server] Pipeline completed without final.mp4; marking job as failed\n",
                    stage=STAGE_ARTIFACT,
                    exit_code=JOB_EXIT_ARTIFACT_ERROR,
                    next_action_hint="Check renderer output directory and ensure final.mp4 is produced.",
                    stage_durations_seconds=stage_durations_seconds,
                )
                return

            db_job.status = "done"
            db_job.progress = 100
            db_job.finished_at = _utcnow()
            db_job.lease_expires_at = None
            self.db.commit()
            self._log_event(db_job, "[server] Job completed successfully", stage="workflow")
            self._append_job_summary(
                db_job,
                status="done",
                failed_stage="none",
                exit_code=JOB_EXIT_SUCCESS,
                total_duration_seconds=self._job_duration_seconds(db_job, db_job.finished_at),
                next_action_hint="No action required.",
                stage_durations_seconds=stage_durations_seconds,
            )
        except Exception as e:
            if self.db.is_active:
                try:
                    db_job = self.get_job(job_id)
                    if db_job:
                        hint = infer_root_cause_hint(STAGE_WORKFLOW, str(e), JOB_EXIT_WORKFLOW_ERROR)
                        self._mark_job_error(
                            db_job,
                            f"[server] Worker error: {e}\n",
                            stage=STAGE_WORKFLOW,
                            exit_code=JOB_EXIT_WORKFLOW_ERROR,
                            next_action_hint=hint,
                            stage_durations_seconds=stage_durations_seconds,
                        )
                except Exception:
                    pass
            self.logger.error(f"Worker error: {e}")
        finally:
            if slot_acquired:
                _release_job_slot()
