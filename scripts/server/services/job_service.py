import os
import sys
import uuid
import time
import subprocess
import threading
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session

from .base import BaseService
from ..models import JobModel
from scripts.server.logger import logger

_LOG_FLUSH_INTERVAL = 5

class JobService(BaseService):
    def create_job(self) -> JobModel:
        job = JobModel(id=str(uuid.uuid4()))
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job(self, job_id: str) -> Optional[JobModel]:
        return self.db.query(JobModel).filter(JobModel.id == job_id).first()

    def start_background_job(self, job_id: str, req_data: dict):
        thread = threading.Thread(target=self._worker, args=(job_id, req_data))
        thread.daemon = True
        thread.start()

    def _append_log(self, db_job: JobModel, text: str, db: Session = None):
        db_session = db or self.db
        db_job.log = (db_job.log or "") + text
        db_session.commit()
        if db_job.out_dir:
            try:
                log_path = Path(db_job.out_dir) / "log.txt"
                with open(log_path, "a", encoding="utf-8", errors="ignore") as f:
                    f.write(text)
            except Exception as e:
                self.logger.error(f"Failed to write to log file: {e}")

    def _flush_log_buffer(self, db_job: JobModel, buf: List[str], db: Session = None):
        if not buf:
            return
        self._append_log(db_job, "".join(buf), db=db)
        buf.clear()

    def _run_and_capture(self, cmd: List[str], cwd: Path, db_job: JobModel, db: Session = None) -> int:
        self._append_log(db_job, f"\n$ {' '.join(cmd)}\n", db=db)
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            assert proc.stdout is not None
            buf: List[str] = []
            line_count = 0
            for line in proc.stdout:
                buf.append(line)
                line_count += 1
                if "[pipeline]" in line:
                    if "Step 1" in line: db_job.progress = 42
                    elif "Step 2" in line: db_job.progress = 50
                    elif "Step 3" in line: db_job.progress = 60
                    elif "Step 4" in line: db_job.progress = 70
                    elif "Step 5" in line: db_job.progress = 85
                    self._flush_log_buffer(db_job, buf, db=db)
                elif line_count % _LOG_FLUSH_INTERVAL == 0:
                    self._flush_log_buffer(db_job, buf, db=db)
            self._flush_log_buffer(db_job, buf, db=db)
            return proc.wait()
        except Exception as e:
            self._append_log(db_job, f"Exception: {e}\n", db=db)
            return 1

    def _worker(self, job_id: str, req_data: dict):
        # Service logic for the background worker
        # Re-importing inside thread to be safe with session scope
        from scripts.server.database import SessionLocal
        from dotenv import load_dotenv
        
        db = SessionLocal()
        try:
            db_job = db.query(JobModel).filter(JobModel.id == job_id).first()
            if not db_job:
                return

            load_dotenv(override=True)
            db_job.status = "running"
            db_job.progress = 5
            db.commit()

            root = Path(__file__).resolve().parents[3]
            out_dir = root / "media" / "videos" / "web_jobs" / db_job.id
            out_dir.mkdir(parents=True, exist_ok=True)
            db_job.out_dir = str(out_dir)
            db.commit()

            python = sys.executable
            plan_path = root / "media" / "texts" / f"solution_plan_{db_job.id}.json"
            db_job.plan_path = str(plan_path)
            db.commit()

            if req_data.get("orchestrate"):
                db_job.progress = 10
                db.commit()
                cmd_1 = [python, "-m", "scripts.orchestrator.run_orchestrator", req_data["problem"], "--out", str(plan_path)]
                mode = req_data.get("mode") or "question_solving"
                cmd_1.extend(["--mode", str(mode)])
                if req_data.get("long_video"):
                    cmd_1.append("--long-video")
                if req_data.get("custom_prompt"):
                    cmd_1.extend(["--prompt", req_data["custom_prompt"]])
                
                self._append_log(db_job, "[server] Starting LLM orchestration...\n", db=db)
                rc1 = self._run_and_capture(cmd_1, root, db_job, db=db)
                if rc1 != 0:
                    self._append_log(db_job, "[server] LLM orchestration failed\n", db=db)
                    db_job.status = "error"
                    db.commit()
                    return
                db_job.progress = 30
                db.commit()

            # Step 2: Pipeline execution (use -m to run as module, not as script)
            cmd_2 = [python, "-m", "scripts.pipeline", "--json", str(plan_path), "--out-dir", str(out_dir)]
            if req_data.get("voice_first"): cmd_2.append("--voice-first")
            if req_data.get("element_audio"): cmd_2.append("--element-audio")

            self._append_log(db_job, "[server] Starting pipeline rendering...\n", db=db)
            rc2 = self._run_and_capture(cmd_2, root, db_job, db=db)
            if rc2 != 0:
                self._append_log(db_job, "[server] Pipeline failed\n", db=db)
                db_job.status = "error"
                db.commit()
                return

            # Finish job
            db_job.status = "done"
            db_job.progress = 100
            db.commit()
            
        except Exception as e:
            self.logger.error(f"Worker error: {e}")
        finally:
            db.close()
