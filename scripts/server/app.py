import os
import sys
import time
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager

from dotenv import load_dotenv
# Load environment variables BEFORE local imports that read env vars at import time
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .database import engine, Base, get_db
from .models import JobModel, User
from .schemas import RunRequest, JobResponse, JobStatusResponse, UserCreate, Token, UserResponse, LoginRequest, ForgotPasswordRequest
from .services.job_service import JobService
from .services.user_service import UserService
from .auth import create_access_token, get_current_user
from .logger import logger

# --- Initialization ---

# Create DB Tables
Base.metadata.create_all(bind=engine)

# Paths
ROOT = Path(__file__).resolve().parents[2]
MEDIA_DIR = ROOT / "media"
VIDEOS_DIR = MEDIA_DIR / "videos"
TEXTS_DIR = MEDIA_DIR / "texts"
WEB_DIR = ROOT / "web"

VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
TEXTS_DIR.mkdir(parents=True, exist_ok=True)
WEB_DIR.mkdir(parents=True, exist_ok=True)

# Cloud Storage
try:
    from scripts.cloud_storage import storage as cloud_storage
except ImportError:
    cloud_storage = None

# --- Lifespan ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    from scripts.server.database import SessionLocal
    db = SessionLocal()
    try:
        # Cleanup orphaned jobs on startup
        orphaned_jobs = db.query(JobModel).filter(JobModel.status == "running").all()
        for j in orphaned_jobs:
            j.status = "error"
            j.log = (j.log or "") + "\n[server] Job abandoned after crash. Marked as failed."
        db.commit()
    finally:
        db.close()
    yield

# --- App Instance ---

# --- Rate Limiter ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Phiversity API", 
    description="Professional-grade video generation API",
    version="1.1.0", 
    lifespan=lifespan
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Middleware ---

# CORS: wildcard origin is incompatible with allow_credentials=True per the spec.
# Use explicit origins from env var; default to localhost only.
_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        "Request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration": f"{duration:.4f}s"
        }
    )
    return response

# --- Dependency Providers ---

def get_job_service(db: Session = Depends(get_db)):
    return JobService(db)

def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)

# --- Endpoints ---

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "ok", 
        "service": "phiversity-api", 
        "version": "1.1.0",
        "timestamp": time.time()
    }

# --- Authentication ---

@app.post("/api/v1/auth/signup", response_model=UserResponse, tags=["Auth"])
async def signup(user_data: UserCreate, service: UserService = Depends(get_user_service)):
    if service.get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = service.create_user(user_data.email, user_data.password)
    return user

@app.post("/api/v1/auth/token", response_model=Token, tags=["Auth"])
async def login(login_data: LoginRequest, service: UserService = Depends(get_user_service)):
    user = service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/auth/me", response_model=UserResponse, tags=["Auth"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/api/v1/auth/guest", response_model=Token, tags=["Auth"])
async def guest_login(service: UserService = Depends(get_user_service)):
    """Create or retrieve a guest account and return a JWT token."""
    import secrets
    from sqlalchemy.exc import IntegrityError

    user = None
    for _ in range(3):
        guest_email = f"guest_{secrets.token_hex(8)}@guest.local"
        guest_password = secrets.token_hex(16)
        try:
            user = service.create_user(guest_email, guest_password)
            break
        except IntegrityError:
            service.db.rollback()
            continue

    if user is None:
        raise HTTPException(status_code=500, detail="Could not create guest session")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/forgot-password", tags=["Auth"])
async def forgot_password(req: ForgotPasswordRequest, service: UserService = Depends(get_user_service)):
    """Check if the email exists. In production, this would send a reset email."""
    user = service.get_user_by_email(req.email)
    # Always return success to avoid email enumeration
    logger.info(f"Password reset requested for {req.email}, exists={user is not None}")
    return {"message": "If this email exists, a reset link will be sent."}

# --- Video Generation ---

@app.post("/api/v1/run", response_model=JobResponse, tags=["Jobs"])
@limiter.limit("5/minute")
async def run_prompt(
    request: Request,
    req: RunRequest,
    service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
    # Idempotency: if a key is provided and a job with that key already exists, return it
    if req.idempotency_key:
        existing = service.db.query(JobModel).filter(
            JobModel.idempotency_key == req.idempotency_key
        ).first()
        if existing:
            return {"job_id": existing.id, "status": existing.status}

    job = service.create_job()
    job.user_id = current_user.id
    if req.idempotency_key:
        job.idempotency_key = req.idempotency_key
    service.db.commit()
    service.start_background_job(job.id, req.dict())
    return {"job_id": job.id, "status": "queued"}

@app.get("/api/v1/jobs", response_model=List[JobResponse], tags=["Jobs"])
async def list_jobs(
    service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
    """List recent jobs for the current user"""
    # Simply return a list of job responses. JobResponse schema already has job_id and status.
    jobs = service.db.query(JobModel).filter(JobModel.user_id == current_user.id).order_by(JobModel.created_at.desc()).limit(10).all()
    return [{"job_id": j.id, "status": j.status} for j in jobs]

@app.get("/api/v1/jobs/{job_id}", response_model=JobStatusResponse, tags=["Jobs"])
async def get_job_status(job_id: str, service: JobService = Depends(get_job_service)):
    db_job = service.get_job(job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    log_content = db_job.log or ""
    if len(log_content) > 10000:
        log_content = "...[truncated]...\n" + log_content[-10000:]
        
    response_data = {
        "status": db_job.status,
        "log": log_content,
        "progress": db_job.progress,
        "video_url": db_job.video_url,
        "plan_url": db_job.plan_url,
    }

    # Format local video paths to static paths
    if db_job.video_path:
        p = Path(db_job.video_path)
        if p.exists():
            try:
                rel = p.relative_to(ROOT / "media")
                response_data["video_url"] = f"/media/{rel.as_posix()}"
            except ValueError:
                pass
                
    if db_job.plan_path:
        p = Path(db_job.plan_path)
        if p.exists():
            try:
                rel = p.relative_to(ROOT / "media")
                response_data["plan_url"] = f"/media/{rel.as_posix()}"
            except ValueError:
                pass
                
    return response_data

# --- Legacy Redirects ---

@app.post("/api/run", tags=["Legacy"])
async def legacy_run(req: RunRequest, service: JobService = Depends(get_job_service)):
    # Legacy endpoint does not require auth for backward compatibility if needed,
    # but strictly speaking, we should enable auth or keep it as-is.
    # We'll allow it for now but note it's deprecated.
    job = service.create_job()
    service.start_background_job(job.id, req.dict())
    return {"job_id": job.id, "status": "queued"}

@app.get("/api/jobs/{job_id}", tags=["Legacy"])
async def legacy_job_status(job_id: str, service: JobService = Depends(get_job_service)):
    return await get_job_status(job_id, service)

# --- Static Mounts ---

app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
