import os
import sys
import json
import uuid
import threading
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional, Any
from fastapi import APIRouter

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env if present; allow overriding existing
load_dotenv(override=True)

# Import cloud storage
try:
    from scripts.cloud_storage import storage as cloud_storage
except ImportError:
    cloud_storage = None

ROOT = Path(__file__).resolve().parents[2]
MEDIA_DIR = ROOT / "media"
VIDEOS_DIR = MEDIA_DIR / "videos"
TEXTS_DIR = MEDIA_DIR / "texts"
WEB_DIR = ROOT / "web"

VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
TEXTS_DIR.mkdir(parents=True, exist_ok=True)
WEB_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Manimations Frontend API")

# Enable CORS for cloud deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

class RunRequest(BaseModel):
    problem: str
    voice_first: bool = True
    element_audio: bool = False
    orchestrate: bool = True
    # Optional: override solver prompt that guides the LLM. When provided,
    # the orchestrator will use this prompt (with the user question appended)
    # instead of auto-generating one via ChatGPT.
    custom_prompt: Optional[str] = None


class Job:
    def __init__(self, job_id: str):
        self.id = job_id
        self.status: str = "queued"  # queued | running | done | error
        self.log: str = ""
        self.video_path: Optional[Path] = None
        self.video_url: Optional[str] = None  # Cloud storage URL
        self.plan_path: Optional[Path] = None
        self.plan_url: Optional[str] = None  # Cloud storage URL
        self.out_dir: Optional[Path] = None
        self.progress: int = 0  # 0-100 percentage
        self._lock = threading.Lock()

    def append_log(self, text: str):
        with self._lock:
            self.log += text
            if self.out_dir:
                try:
                    log_path = self.out_dir / "log.txt"
                    with open(log_path, "a", encoding="utf-8", errors="ignore") as f:
                        f.write(text)
                except Exception:
                    pass

    def set_status(self, status: str):
        with self._lock:
            self.status = status

    def set_video(self, path: Optional[Path]):
        with self._lock:
            self.video_path = path

    def set_plan(self, path: Optional[Path]):
        with self._lock:
            self.plan_path = path

    def set_out_dir(self, path: Optional[Path]):
        with self._lock:
            self.out_dir = path

    def set_progress(self, percent: int):
        with self._lock:
            self.progress = max(0, min(100, percent))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.id,
            "status": self.status,
            "video_path": str(self.video_path) if self.video_path else None,
            "plan_path": str(self.plan_path) if self.plan_path else None,
            "out_dir": str(self.out_dir) if self.out_dir else None,
            "progress": self.progress,
        }


class JobManager:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self) -> Job:
        job_id = uuid.uuid4().hex[:12]
        job = Job(job_id)
        with self._lock:
            self.jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Job:
        job = self.jobs.get(job_id)
        if not job:
            raise KeyError(job_id)
        return job


jobs = JobManager()


def _run_and_capture(cmd: list[str], cwd: Path, job: Job) -> int:
    job.append_log(f"\n$ {' '.join(cmd)}\n")
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            job.append_log(line)
        return proc.wait()
    except Exception as e:
        job.append_log(f"Exception: {e}\n")
        return 1


def _find_newest_mp4(base_dir: Path) -> Optional[Path]:
    newest: Optional[Path] = None
    newest_mtime = -1.0
    for root, _dirs, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith(".mp4"):
                p = Path(root) / f
                try:
                    mtime = p.stat().st_mtime
                    if mtime > newest_mtime:
                        newest_mtime = mtime
                        newest = p
                except FileNotFoundError:
                    continue
    return newest


def _worker(job: Job, req: RunRequest):
    # Refresh .env on each job in case keys changed
    load_dotenv(override=True)
    job.set_status("running")
    job.set_progress(5)  # Job started
    # Initialize job directory and persist initial state
    out_dir = VIDEOS_DIR / "web_jobs" / job.id
    out_dir.mkdir(parents=True, exist_ok=True)
    job.set_out_dir(out_dir)
    
    # Overall job timeout (default 20 minutes)
    job_timeout = int(os.getenv("JOB_TIMEOUT", "1200"))
    start_time = time.time()
    
    try:
        python = sys.executable
        plan_path = TEXTS_DIR / f"solution_plan_{job.id}.json"
        job.set_plan(plan_path)
        _persist_job(job)

        if req.orchestrate:
            job.set_progress(10)  # Starting orchestration
            cmd_1 = [
                python,
                "-m",
                "scripts.orchestrator.run_orchestrator",
                req.problem,
                "--out",
                str(plan_path),
            ]
            default_prompt_path = ROOT / "Prompt.txt"
            if req.custom_prompt:
                # If custom_prompt is a readable file path, use --prompt-file; otherwise use --prompt
                try:
                    pth = Path(req.custom_prompt)
                    if pth.exists() and pth.is_file():
                        cmd_1.extend(["--prompt-file", str(pth)])
                    else:
                        cmd_1.extend(["--prompt", req.custom_prompt])
                except Exception:
                    cmd_1.extend(["--prompt", req.custom_prompt])
            else:
                # Fallback: use Prompt.txt at workspace root if present
                try:
                    if default_prompt_path.exists():
                        cmd_1.extend(["--prompt-file", str(default_prompt_path)])
                except Exception:
                    pass
            job.append_log("[server] Starting LLM orchestration...\n")
            rc1 = _run_and_capture(cmd_1, ROOT, job)
            if rc1 != 0:
                job.append_log("[server] Orchestration failed\n")
                job.set_status("error")
                return
            
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > job_timeout:
                job.append_log(f"[server] Job timeout exceeded ({elapsed:.1f}s > {job_timeout}s)\n")
                job.set_status("error")
                return
            job.set_progress(30)  # Orchestration completed
            job.append_log(f"[server] Orchestration completed ({elapsed:.1f}s elapsed)\n")
        else:
            # If not orchestrating, assume problem contains a path to plan JSON
            try:
                plan_candidate = Path(req.problem)
                if plan_candidate.exists():
                    plan_path = plan_candidate
                    job.set_plan(plan_path)
                else:
                    job.append_log(f"No orchestration and plan path invalid: {plan_candidate}\n")
                    job.set_status("error")
                    return
            except Exception:
                job.append_log("Invalid plan path when orchestrate=False.\n")
                job.set_status("error")
                return

        job.set_progress(40)
        cmd_2 = [
            python,
            "-m",
            "scripts.pipeline",
            "--json",
            str(plan_path),
            "--out-dir",
            str(out_dir),
        ]
        if req.voice_first:
            cmd_2.append("--voice-first")
        if req.element_audio:
            cmd_2.append("--element-audio")

        job.append_log("[server] Starting video generation pipeline...\n")
        rc2 = _run_and_capture(cmd_2, ROOT, job)
        
        # Check timeout
        elapsed = time.time() - start_time
        if elapsed > job_timeout:
            job.append_log(f"[server] Job timeout exceeded ({elapsed:.1f}s > {job_timeout}s)\n")
            job.set_status("error")
            _persist_job(job)
            return
            
        if rc2 != 0:
            job.append_log("[server] Pipeline execution failed\n")
            job.set_status("error")
            _persist_job(job)
            return
        
        job.set_progress(90)  # Pipeline completed
        job.append_log(f"[server] Pipeline completed ({elapsed:.1f}s total)\n")

        # Pipeline writes final.mp4 in out_dir
        final_path = out_dir / "final.mp4"
        if not final_path.exists():
            # Fallback: scan videos dir
            time.sleep(0.5)
            # Prefer to search within this job's out_dir only
            final_scan = _find_newest_mp4(out_dir)
            if final_scan is None:
                job.append_log("Could not find output video.\n")
                job.set_status("error")
                return
            job.set_video(final_scan)
        else:
            job.set_video(final_path)
        
        # Upload to cloud storage if configured
        if cloud_storage and cloud_storage.backend != "local":
            job.append_log("[server] Uploading video to cloud storage...\n")
            try:
                video_url = cloud_storage.upload_video(final_path, job.id)
                job.video_url = video_url
                job.append_log(f"[server] Video uploaded: {video_url}\n")
                
                # Upload plan JSON too
                if job.plan_path and job.plan_path.exists():
                    plan_url = cloud_storage.upload_json(job.plan_path, job.id)
                    job.plan_url = plan_url
            except Exception as e:
                job.append_log(f"[server] Cloud upload warning: {e}\n")
        
        total_elapsed = time.time() - start_time
        job.append_log(f"[server] Job completed successfully in {total_elapsed:.1f}s\n")
        job.set_progress(100)  # Job completed
        job.set_status("done")
        _persist_job(job)
    except Exception as e:
        elapsed = time.time() - start_time
        job.append_log(f"[server] Unhandled exception after {elapsed:.1f}s: {e}\n")
        job.set_status("error")
        _persist_job(job)
        
@app.get("/health")
def health_check():
    """Health check endpoint for cloud platforms"""
    return {"status": "ok", "service": "manimations-api"}

@app.post("/api/run")
def run(req: RunRequest):
    job = jobs.create()
    t = threading.Thread(target=_worker, args=(job, req), daemon=True)
    t.start()
    return {"job_id": job.id}

@app.get("/api/jobs/{job_id}")
def job_status(job_id: str):
    try:
        job = jobs.get(job_id)
    except KeyError:
        # Attempt to recover from disk persistence (e.g., after server reload)
        disk_dir = VIDEOS_DIR / "web_jobs" / job_id
        state_path = disk_dir / "job.json"
        if not state_path.exists():
            raise HTTPException(status_code=404, detail="Job not found")
        try:
            data = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            raise HTTPException(status_code=404, detail="Job not found")
        # Build response directly from persisted data
        video_path = data.get("video_path")
        plan_path = data.get("plan_path")
        video_url = None
        plan_url = None
        log_url = None
        if video_path:
            vp = Path(video_path)
            if vp.exists():
                try:
                    rel = vp.relative_to(MEDIA_DIR)
                    video_url = f"/media/{rel.as_posix()}"
                except ValueError:
                    video_url = str(vp)
        if plan_path:
            pp = Path(plan_path)
            if pp.exists():
                try:
                    rel = pp.relative_to(MEDIA_DIR)
                    plan_url = f"/media/{rel.as_posix()}"
                except ValueError:
                    plan_url = str(pp)
        # Tail of log file if present; also expose a URL if under /media
        log_tail = ""
        log_file = disk_dir / "log.txt"
        if log_file.exists():
            try:
                content = log_file.read_text(encoding="utf-8", errors="ignore")
                max_chars = 10000
                log_tail = content[-max_chars:] if len(content) > max_chars else content
            except Exception:
                log_tail = ""
            try:
                rel = log_file.relative_to(MEDIA_DIR)
                log_url = f"/media/{rel.as_posix()}"
            except ValueError:
                log_url = str(log_file)
        return JSONResponse(
            content={
                "job_id": job_id,
                "status": data.get("status", "error"),
                "progress": data.get("progress", 0),
                "video_url": video_url,
                "plan_path": plan_path,
                "plan_url": plan_url,
                "log_url": log_url,
                "log": log_tail,
            }
        )

    video_url = None
    if job.video_path and job.video_path.exists():
        # Prioritize cloud URL if available
        if job.video_url:
            video_url = job.video_url
        else:
            # Expose under /media
            try:
                rel = job.video_path.relative_to(MEDIA_DIR)
                video_url = f"/media/{rel.as_posix()}"
            except ValueError:
                # Not under media; fallback to absolute path disclosure (not preferred)
                video_url = str(job.video_path)

    # Return tail of the log to keep payload small
    log = job.log
    max_chars = 10000
    if len(log) > max_chars:
        log = "..." + log[-max_chars:]

    # Derive plan_url if plan exists
    plan_url = None
    if job.plan_path and job.plan_path.exists():
        try:
            relp = job.plan_path.relative_to(MEDIA_DIR)
            plan_url = f"/media/{relp.as_posix()}"
        except ValueError:
            plan_url = str(job.plan_path)

    # Derive log_url if log exists in out_dir
    log_url = None
    if job.out_dir:
        lf = job.out_dir / "log.txt"
        if lf.exists():
            try:
                rell = lf.relative_to(MEDIA_DIR)
                log_url = f"/media/{rell.as_posix()}"
            except ValueError:
                log_url = str(lf)

    return JSONResponse(
        content={
            "job_id": job.id,
            "status": job.status,
            "progress": job.progress,
            "video_url": video_url,
            "plan_path": str(job.plan_path) if job.plan_path else None,
            "plan_url": plan_url,
            "log_url": log_url,
            "log": log,
        }
    )


# Static mounts: media and web
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")


def _persist_job(job: Job):
    # Write job state and append logs to disk so we can recover after reloads
    if not job.out_dir:
        return
    try:
        job.out_dir.mkdir(parents=True, exist_ok=True)
        state_path = job.out_dir / "job.json"
        state_path.write_text(json.dumps(job.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
