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

# Consistent naming for video outputs
# All final videos from the pipeline are named "final.mp4" for consistency
FINAL_VIDEO_NAME = "final.mp4"

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from scripts.orchestrator.prompt_orchestrator import (
    call_gemini_solver,
    call_groq_solver,
    call_openrouter_solver,
)

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
# Default to localhost:8001 for development; override with CORS_ORIGINS env var for production
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8001,http://localhost:3000,http://127.0.0.1:8001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
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
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "problem": "Explain conservation of angular momentum",
                    "voice_first": True,
                    "orchestrate": True
                }
            ]
        }
    
    def validate_inputs(self):
        """Validate input constraints"""
        if not self.problem or len(self.problem) > 5000:
            raise ValueError("Problem must be 1-5000 characters")
        if self.custom_prompt and len(self.custom_prompt) > 10000:
            raise ValueError("Custom prompt must be under 10000 characters")


class LlmTestRequest(BaseModel):
    question: str
    provider: str
    prompt_text: Optional[str] = None
    use_prompt_file: bool = True

    def validate_inputs(self):
        if not self.question or len(self.question) > 5000:
            raise ValueError("Question must be 1-5000 characters")
        if self.prompt_text and len(self.prompt_text) > 20000:
            raise ValueError("Prompt must be under 20000 characters")


class Job:
    def __init__(self, job_id: str):
        self.id = job_id
        self.status: str = "queued"  # queued | running | completed | failed
        self.error: str = ""  # Error message if status is failed
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

    def set_error(self, error: str):
        with self._lock:
            self.error = error

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

    def get_stage(self) -> str:
        """Return stage text based on current progress percentage"""
        if self.progress < 25:
            return "Setting up video generation"
        elif self.progress < 50:
            return "Processing AI orchestration"
        elif self.progress < 75:
            return "Rendering animations"
        elif self.progress < 100:
            return "Finalizing video"
        else:
            return "Completed"

    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "job_id": self.id,
                "status": self.status,
                "error": self.error,
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
        with self._lock:
            job = self.jobs.get(job_id)
            if not job:
                raise KeyError(job_id)
            return job


jobs = JobManager()


def _run_and_capture(cmd: list[str], cwd: Path, job: Job) -> int:
    job.append_log(f"\n$ {' '.join(cmd)}\n")
    try:
        # Create environment for subprocess
        # Start with current environment to avoid Python initialization errors
        # but remove PYTHONPATH which can cause conflicts with system Python
        env = os.environ.copy()
        
        # Remove PYTHONPATH to allow subprocess to use its own Python paths
        env.pop('PYTHONPATH', None)
        
        # Ensure encoding is set for proper stream initialization
        if 'PYTHONIOENCODING' not in env:
            env['PYTHONIOENCODING'] = 'utf-8'
        
        # CRITICAL: Force unbuffered output so parent process sees real-time logs
        env['PYTHONUNBUFFERED'] = '1'
        
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdin=subprocess.DEVNULL,  # Prevent subprocess from blocking on input
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=env,
        )
        assert proc.stdout is not None
        line_count = 0
        for line in proc.stdout:
            job.append_log(line)
            line_count += 1
            # Log every 50th line to show progress in long-running processes
            if line_count % 50 == 0:
                job.append_log(f"[server] [progress] {line_count} lines from subprocess\n")
        # Add timeout to prevent indefinite wait (use env var or default 15 minutes)
        subprocess_timeout = int(os.getenv("SUBPROCESS_TIMEOUT", "900"))
        try:
            return_code = proc.wait(timeout=subprocess_timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()  # Clean up zombie process
            job.append_log(f"\n[server] ERROR: Subprocess exceeded {subprocess_timeout}s timeout and was killed\n")
            return 1
        return return_code
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


def _get_stage_from_progress(progress: int) -> str:
    """Return stage text based on current progress percentage"""
    if progress < 25:
        return "Setting up video generation"
    elif progress < 50:
        return "Processing AI orchestration"
    elif progress < 75:
        return "Rendering animations"
    elif progress < 100:
        return "Finalizing video"
    else:
        return "Completed"


def _load_prompt_text(req: LlmTestRequest) -> str:
    if req.prompt_text and req.prompt_text.strip():
        return req.prompt_text.strip()
    if req.use_prompt_file:
        for name in ("Prompt.txt", "prompt.txt"):
            pth = ROOT / name
            if pth.exists():
                return pth.read_text(encoding="utf-8", errors="ignore").strip()
    return ""


def _build_solver_prompt(question: str, prompt_text: str) -> str:
    if prompt_text:
        return prompt_text + "\n\n" + f"User question: {question.strip()}"
    return question.strip()


def _get_provider_model_name(provider: str) -> str:
    if provider == "gemini":
        return os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
    if provider == "groq":
        return os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
    if provider == "openrouter":
        return os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-70b-instruct")
    return "unknown"


def _worker(job: Job, req: RunRequest):
    # Refresh .env on each job in case keys changed
    load_dotenv(override=True)
    job.set_status("running")
    job.set_progress(5)  # Job started
    # Initialize job directory and persist initial state
    out_dir = VIDEOS_DIR / "web_jobs" / job.id
    out_dir.mkdir(parents=True, exist_ok=True)
    job.set_out_dir(out_dir)
    
    # Overall job timeout (default 15 minutes)
    job_timeout = int(os.getenv("JOB_TIMEOUT", "900"))
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
                    pth = Path(req.custom_prompt).resolve()
                    # Ensure path is within project root to prevent directory traversal
                    if pth.is_relative_to(ROOT) and pth.is_file():
                        cmd_1.extend(["--prompt-file", str(pth)])
                    else:
                        cmd_1.extend(["--prompt", req.custom_prompt])
                except (ValueError, Exception):
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
                err_msg = "Orchestration failed - LLM service encountered an error"
                job.append_log(f"[server] {err_msg}\n")
                job.set_error(err_msg)
                job.set_status("failed")
                return
            
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > job_timeout:
                err_msg = f"Job timeout exceeded ({elapsed:.1f}s > {job_timeout}s)"
                job.append_log(f"[server] {err_msg}\n")
                job.set_error(err_msg)
                job.set_status("failed")
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
                    err_msg = f"Plan file not found: {plan_candidate}"
                    job.append_log(f"{err_msg}\n")
                    job.set_error(err_msg)
                    job.set_status("failed")
                    return
            except Exception as e:
                err_msg = f"Invalid plan path: {str(e)}"
                job.append_log(f"{err_msg}\n")
                job.set_error(err_msg)
                job.set_status("failed")
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
            err_msg = f"Job timeout exceeded ({elapsed:.1f}s > {job_timeout}s)"
            job.append_log(f"[server] {err_msg}\n")
            job.set_error(err_msg)
            job.set_status("failed")
            _persist_job(job)
            return
            
        if rc2 != 0:
            err_msg = "Video rendering pipeline failed"
            job.append_log(f"[server] {err_msg}\n")
            job.set_error(err_msg)
            job.set_status("failed")
            _persist_job(job)
            return
        
        job.set_progress(90)  # Pipeline completed
        job.append_log(f"[server] Pipeline completed ({elapsed:.1f}s total)\n")

        # Pipeline writes final.mp4 in out_dir (strict naming)
        final_path = out_dir / FINAL_VIDEO_NAME
        
        # Verify the exact file exists
        if not final_path.exists():
            job.append_log(f"[server] ERROR: Expected final video not found at {final_path}\n")
            # Debug: list files in out_dir
            if out_dir.exists():
                files = list(out_dir.glob("*.mp4"))
                if files:
                    job.append_log(f"[server] Found video files: {[f.name for f in files]}\n")
                    # Try to use the most recent one as fallback
                    newest = max(files, key=lambda f: f.stat().st_mtime)
                    job.append_log(f"[server] Using fallback video: {newest.name}\n")
                    job.set_video(newest)
                else:
                    err_msg = "No video files found in output directory"
                    job.append_log(f"[server] {err_msg}\n")
                    job.set_error(err_msg)
                    job.set_status("failed")
                    _persist_job(job)
                    return
            else:
                err_msg = f"Output directory does not exist: {out_dir}"
                job.append_log(f"[server] {err_msg}\n")
                job.set_error(err_msg)
                job.set_status("failed")
                _persist_job(job)
                return
        else:
            job.append_log(f"[server] Final video confirmed: {final_path} ({final_path.stat().st_size / 1024 / 1024:.1f} MB)\n")
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
        job.set_status("completed")
        _persist_job(job)
    except Exception as e:
        elapsed = time.time() - start_time
        err_msg = f"Unhandled exception: {str(e)}"
        job.append_log(f"[server] {err_msg} after {elapsed:.1f}s\n")
        job.set_error(err_msg)
        job.set_status("failed")
        _persist_job(job)
        
@app.get("/health")
def health_check():
    """Health check endpoint for cloud platforms"""
    return {"status": "ok", "service": "manimations-api"}

@app.post("/api/run")
def run(req: RunRequest):
    try:
        req.validate_inputs()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    job = jobs.create()
    t = threading.Thread(target=_worker, args=(job, req), daemon=True)
    t.start()
    return {
        "job_id": job.id,
        "status_url": f"/api/jobs/{job.id}",
    }


@app.post("/api/llm-test")
def llm_test(req: LlmTestRequest):
    try:
        req.validate_inputs()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    provider = (req.provider or "").strip().lower()
    if provider not in {"gemini", "groq", "openrouter"}:
        raise HTTPException(status_code=400, detail="Invalid provider")

    prompt_text = _load_prompt_text(req)
    solver_prompt = _build_solver_prompt(req.question, prompt_text)

    start = time.time()
    try:
        if provider == "gemini":
            output = call_gemini_solver(solver_prompt, context_question=req.question)
        elif provider == "groq":
            output = call_groq_solver(solver_prompt, context_question=req.question)
        else:
            output = call_openrouter_solver(solver_prompt, context_question=req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    elapsed_ms = int((time.time() - start) * 1000)
    return {
        "provider": provider,
        "model": _get_provider_model_name(provider),
        "elapsed_ms": elapsed_ms,
        "output": output,
    }

@app.get("/api/jobs/{job_id}")
def job_status(job_id: str):
    # Validate job_id is alphanumeric to prevent path traversal
    if not job_id.isalnum() or len(job_id) > 20:
        raise HTTPException(status_code=400, detail="Invalid job_id")
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
                "status": data.get("status", "failed"),
                "error": data.get("error", ""),
                "progress": data.get("progress", 0),
                "stage": _get_stage_from_progress(data.get("progress", 0)),
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
            "error": job.error,
            "progress": job.progress,
            "stage": job.get_stage(),
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
