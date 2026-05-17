import os
import sys
import time
import asyncio
import json
import hashlib
import base64
import secrets
import re
import requests
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, List, Any
from contextlib import asynccontextmanager, suppress
from urllib.parse import urlencode

from dotenv import load_dotenv
# Load environment variables BEFORE local imports that read env vars at import time
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Response as FastAPIResponse

# Cookie configuration constants
REFRESH_TOKEN_COOKIE_NAME = "phiversity_refresh"
CSRF_TOKEN_COOKIE_NAME = "phiversity_csrf"
COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 days in seconds


def _get_cookie_settings() -> dict:
    """Get secure cookie settings based on environment."""
    is_production = os.getenv("PHIVERSITY_ENV") in {"prod", "production", "staging"}
    return {
        "httponly": True,
        "secure": is_production,
        "samesite": "strict" if is_production else "lax",
        "max_age": COOKIE_MAX_AGE,
        "path": "/",
    }
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .database import (
    engine,
    Base,
    get_db,
    ensure_required_schema_ready,
    missing_required_schema,
    schema_readiness_required,
)
from .models import (
    JobModel,
    User,
    QualityTier,
    UserRole,
    AuthIdentity,
    UserProfile,
    RefreshToken,
    SecurityEvent,
    PasswordlessLoginToken,
    OAuthClient,
    OAuthAuthorizationCode,
    WebAuthnCredential,
    SAMLIdentityProvider,
    PaymentAccount,
    Subscription,
    PaymentInvoice,
    PaymentTransaction,
)
from .schemas import (
    RunRequest,
    JobResponse,
    JobStatusResponse,
    JobSummaryResponse,
    UserCreate,
    Token,
    UserResponse,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RefreshTokenRequest,
    LogoutRequest,
    MFAConfirmRequest,
    MFABackupRequest,
    APIKeyCreateRequest,
    APIKeyVerifyRequest,
    APIKeyRevokeRequest,
    PasswordlessRequest,
    PasswordlessVerifyRequest,
    OAuthClientCreateRequest,
    WebAuthnRegisterVerifyRequest,
    WebAuthnAuthenticateRequest,
    SAMLProviderCreateRequest,
    SAMLACSRequest,
)
from .services.job_service import JobService, _job_execution_mode
from .services.user_service import UserService
from .services.audit_service import AuditService
from .services.password_validator import validate_password_strength, get_password_strength_feedback
from .services.email_verification_service import EmailVerificationService
from .services.mfa_service import MFAService
from .services.api_key_service import APIKeyService
from .services.security_event_service import SecurityEventService
from .services.passwordless_service import PasswordlessService
from .services.oauth_scaffold_service import OAuthScaffoldService
from .services.notification_service import NotificationService
from .services.billing_service import BillingService
from .csrf_protection import CSRFProtection, generate_csrf_token
from .cookie_manager import HttpOnlyCookieManager
from .jwt_key_rotation import JWTKeyRing
from .auth import get_current_user, oauth2_scheme, parse_access_token, create_access_token
from .logger import logger

# --- Initialization ---


def _request_logging_enabled() -> bool:
    return os.getenv("DISABLE_REQUEST_LOGS", "").strip().lower() not in {"1", "true", "yes", "on"}


_SQL_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SQL_COLUMN_TYPE_RE = re.compile(r"^[A-Z]+(?:\s+DEFAULT\s+(?:'[^']*'|[0-9]+))?$")


def _safe_add_column(conn, table_name: str, col_name: str, col_type: str) -> None:
    if table_name not in {"users", "jobs"}:
        raise RuntimeError(f"Refusing schema update for unexpected table: {table_name}")
    if not _SQL_IDENTIFIER_RE.fullmatch(col_name):
        raise RuntimeError(f"Unsafe column identifier: {col_name}")
    if not _SQL_COLUMN_TYPE_RE.fullmatch(col_type):
        raise RuntimeError(f"Unsafe column type definition for {table_name}.{col_name}")

    conn.execute(text(f'ALTER TABLE "{table_name}" ADD COLUMN "{col_name}" {col_type}'))


def _mask_email(email: Optional[str]) -> str:
    normalized = (email or "").strip()
    if not normalized:
        return "***"
    local, _, domain = normalized.partition("@")
    if not domain:
        return "***"
    local_masked = (local[:2] + "***") if len(local) > 2 else "***"
    domain_head = domain.split(".")[0]
    domain_tail = ".".join(domain.split(".")[1:])
    domain_masked = (domain_head[:1] + "***") if domain_head else "***"
    if domain_tail:
        return f"{local_masked}@{domain_masked}.{domain_tail}"
    return f"{local_masked}@{domain_masked}"


def _is_path_within(base_dir: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(base_dir)
        return True
    except ValueError:
        return False


def _resolve_local_path(raw_path: Path) -> Optional[Path]:
    try:
        candidate = raw_path if raw_path.is_absolute() else (ROOT / raw_path)
        resolved = candidate.resolve(strict=False)
        root_resolved = ROOT.resolve(strict=False)
        if not _is_path_within(root_resolved, resolved):
            return None
        return resolved
    except Exception:
        return None


def _resolve_artifact_path(
    raw_path: Path,
    *,
    allowed_suffixes: set[str],
    out_dir: Optional[Path] = None,
) -> Optional[Path]:
    resolved = _resolve_local_path(raw_path)
    if not resolved or not resolved.exists() or not resolved.is_file():
        return None

    suffix = resolved.suffix.lower()
    if suffix not in allowed_suffixes:
        return None

    allowed_roots = [MEDIA_DIR.resolve(strict=False)]
    if out_dir:
        resolved_out_dir = _resolve_local_path(out_dir)
        if resolved_out_dir and resolved_out_dir.exists() and resolved_out_dir.is_dir():
            allowed_roots.append(resolved_out_dir)

    if any(_is_path_within(base_dir, resolved) for base_dir in allowed_roots):
        return resolved
    return None

def _ensure_development_schema_compatibility() -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    with engine.begin() as conn:
        if "users" in table_names:
            existing_user_cols = {col["name"] for col in inspector.get_columns("users")}
            user_missing_cols = [
                ("password_hash_scheme", "VARCHAR DEFAULT 'argon2'"),
                ("password_hash_updated_at", "DATETIME"),
                ("quality_tier", "VARCHAR DEFAULT 'FREE'"),
                ("watermark_enabled", "BOOLEAN DEFAULT 1"),
                ("email_verified", "BOOLEAN DEFAULT 0"),
                ("email_verified_at", "DATETIME"),
                ("password_changed_at", "DATETIME"),
                ("failed_login_attempts", "INTEGER DEFAULT 0"),
                ("locked_until", "DATETIME"),
                ("mfa_enabled", "BOOLEAN DEFAULT 0"),
                ("mfa_secret_encrypted", "TEXT"),
                ("mfa_backup_codes_encrypted", "TEXT"),
                ("last_login_ip", "VARCHAR"),
                ("last_login_at", "DATETIME"),
            ]
            for col_name, col_type in user_missing_cols:
                if col_name not in existing_user_cols:
                    _safe_add_column(conn, "users", col_name, col_type)
            conn.execute(text("UPDATE users SET quality_tier = 'FREE' WHERE quality_tier IS NULL"))
            conn.execute(text("UPDATE users SET watermark_enabled = 1 WHERE watermark_enabled IS NULL"))
            conn.execute(text("UPDATE users SET failed_login_attempts = 0 WHERE failed_login_attempts IS NULL"))
            conn.execute(text("UPDATE users SET password_hash_scheme = 'argon2' WHERE password_hash_scheme IS NULL"))
            conn.execute(text("UPDATE users SET password_hash_updated_at = created_at WHERE password_hash_updated_at IS NULL"))

        if "jobs" in table_names:
            existing_job_cols = {col["name"] for col in inspector.get_columns("jobs")}
            job_missing_cols = [
                ("request_payload", "TEXT"),
                ("attempt_count", "INTEGER DEFAULT 0"),
                ("worker_id", "VARCHAR"),
                ("claimed_at", "DATETIME"),
                ("started_at", "DATETIME"),
                ("finished_at", "DATETIME"),
                ("lease_expires_at", "DATETIME"),
                ("log_path", "VARCHAR"),
                ("log_url", "VARCHAR"),
            ]
            for col_name, col_type in job_missing_cols:
                if col_name not in existing_job_cols:
                    _safe_add_column(conn, "jobs", col_name, col_type)
            conn.execute(text("UPDATE jobs SET attempt_count = 0 WHERE attempt_count IS NULL"))


if schema_readiness_required():
    ensure_required_schema_ready(engine)
else:
    Base.metadata.create_all(bind=engine)
    _ensure_development_schema_compatibility()

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


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


AUTH_TOKEN_CLEANUP_INTERVAL_SECONDS = max(60, _env_int("AUTH_TOKEN_CLEANUP_INTERVAL_SECONDS", 1800))
AUTH_TOKEN_REVOKED_RETENTION_SECONDS = max(0, _env_int("AUTH_TOKEN_REVOKED_RETENTION_SECONDS", 86400))
CSRF_PROTECTED_PATHS = (
    "/api/v1/auth/refresh",
    "/api/v1/auth/logout",
)


def _run_auth_cleanup_once() -> None:
    from scripts.server.database import SessionLocal

    db = SessionLocal()
    try:
        service = UserService(db)
        deleted = service.cleanup_expired_auth_records(
            revoked_retention_seconds=AUTH_TOKEN_REVOKED_RETENTION_SECONDS
        )
        deleted["passwordless_tokens"] = PasswordlessService(db).cleanup_expired()
        deleted.update(JobService(db).cleanup_old_artifact_logs())
        if any(deleted.values()):
            logger.info("Auth token cleanup completed", extra=deleted)
    except Exception as e:
        db.rollback()
        logger.exception("Auth token cleanup failed", exc_info=e)
    finally:
        db.close()


def _ensure_bootstrap_admin_user() -> None:
    """Create a development bootstrap admin account when configured."""
    if not _env_bool("AUTO_CREATE_ADMIN", default=True):
        return

    admin_email = (os.getenv("ADMIN_EMAIL", "admin@phiversity.local") or "").strip().lower()
    admin_password = (os.getenv("ADMIN_PASSWORD", "PhiversityAdmin@123") or "").strip()

    if not admin_email or not admin_password:
        logger.warning("Admin bootstrap skipped: ADMIN_EMAIL or ADMIN_PASSWORD is empty")
        return

    is_production = os.getenv("PHIVERSITY_ENV") in {"prod", "production", "staging"}
    if is_production and admin_password == "PhiversityAdmin@123":
        logger.warning(
            "Admin bootstrap skipped in production because ADMIN_PASSWORD is using the default value"
        )
        return

    from scripts.server.database import SessionLocal

    def _ensure_local_admin_identity(db: Session, user: User, admin_email: str) -> None:
        identity = (
            db.query(AuthIdentity)
            .filter(
                AuthIdentity.user_id == user.id,
                AuthIdentity.provider == "local",
            )
            .first()
        )
        if not identity:
            identity = AuthIdentity(
                user_id=user.id,
                provider="local",
                provider_user_id=admin_email,
                provider_email=admin_email,
                is_primary=True,
                is_verified=True,
            )
            db.add(identity)
            return

        identity.provider_user_id = admin_email
        identity.provider_email = admin_email
        identity.is_primary = True
        identity.is_verified = True

    db = SessionLocal()
    try:
        service = UserService(db)
        existing = service.get_user_by_email(admin_email)
        if existing:
            if existing.role != UserRole.ADMIN:
                existing.role = UserRole.ADMIN
            _ensure_local_admin_identity(db, existing, admin_email)
            db.commit()
            logger.info(
                "Bootstrap admin role/identity ensured for existing user",
                extra={"email": _mask_email(admin_email)},
            )
            return

        created = service.create_user(admin_email, admin_password, role=UserRole.ADMIN)
        _ensure_local_admin_identity(db, created, admin_email)
        db.commit()
        logger.warning(
            "Bootstrap admin account created. Change ADMIN_PASSWORD after first login.",
            extra={"email": _mask_email(admin_email)},
        )
    except Exception as e:
        db.rollback()
        logger.exception("Admin bootstrap failed", exc_info=e)
    finally:
        db.close()


async def _periodic_auth_cleanup_loop() -> None:
    while True:
        await asyncio.sleep(AUTH_TOKEN_CLEANUP_INTERVAL_SECONDS)
        _run_auth_cleanup_once()

@asynccontextmanager
async def lifespan(app: FastAPI):
    from scripts.server.database import SessionLocal
    db = SessionLocal()
    cleanup_task = None
    try:
        # Ensure development admin credentials are available when configured.
        _ensure_bootstrap_admin_user()

        # Re-queue interrupted jobs so a dedicated worker can recover them after restarts.
        JobService(db).recover_interrupted_jobs(reason="server restart")

        # Run one auth cleanup pass immediately at startup.
        _run_auth_cleanup_once()

        # Continue cleanup in the background.
        cleanup_task = asyncio.create_task(_periodic_auth_cleanup_loop())

        # Initialize key ring so rotation schedule is available immediately.
        JWTKeyRing().get_key_rotation_schedule()
    finally:
        db.close()
    try:
        yield
    finally:
        if cleanup_task:
            cleanup_task.cancel()
            with suppress(asyncio.CancelledError):
                await cleanup_task

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
async def add_security_headers(request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Content Security Policy - prevents XSS and data injection
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "  # Necessary for current frontend architecture
        "style-src 'self' 'unsafe-inline'; "   # Necessary for current frontend architecture
        "img-src 'self' data: blob:; "
        "media-src 'self' blob:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    
    # HSTS - Force HTTPS (only enable in production)
    if os.getenv("PHIVERSITY_ENV") in {"prod", "production", "staging"}:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    # X-Frame-Options - Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # X-Content-Type-Options - Prevent MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Referrer-Policy - Control referrer information
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions-Policy - Restrict browser features
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), magnetometer=(), microphone=(), usb=()"
    )
    
    # X-Permitted-Cross-Domain-Policies - Disable Flash/Silverlight cross-domain requests
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    
    # X-XSS-Protection - Legacy XSS protection (modern browsers use CSP)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response


@app.middleware("http")
async def csrf_protection_middleware(request: Request, call_next):
    """Apply CSRF checks only to cookie-auth state-changing endpoints."""
    has_bearer_auth = (request.headers.get("authorization") or "").lower().startswith("bearer ")
    has_refresh_cookie = HttpOnlyCookieManager.REFRESH_TOKEN_COOKIE in request.cookies
    if (
        request.method not in CSRFProtection.SAFE_METHODS
        and request.url.path in CSRF_PROTECTED_PATHS
        and not has_bearer_auth
        and has_refresh_cookie
    ):
        try:
            await CSRFProtection.verify_csrf_token(request)
        except HTTPException:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF token invalid or missing"},
            )

    return await call_next(request)


@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)

    if not _request_logging_enabled():
        return response

    duration = time.time() - start_time
    
    # Security audit logging for auth events
    path = request.url.path
    if path.startswith("/api/v1/auth/"):
        logger.info(
            "Auth event",
            extra={
                "event_type": path.split("/")[-1],
                "method": request.method,
                "status": response.status_code,
                "ip": request.client.host if request.client else None,
            }
        )
    
    logger.info(
        "Request processed",
        extra={
            "method": request.method,
            "path": path,
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


def _require_admin(current_user: User) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def _scoped_idempotency_key(user_id: int, raw_key: Optional[str]) -> Optional[str]:
    if not raw_key:
        return None
    return f"{user_id}:{raw_key}"


def _get_owned_job_or_404(job_id: str, service: JobService, current_user: User) -> JobModel:
    db_job = service.get_job(job_id)
    if not db_job or db_job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job


def _job_video_path(db_job: JobModel) -> Optional[Path]:
    out_dir = Path(db_job.out_dir) if db_job.out_dir else None
    candidates = []
    if db_job.video_path:
        if db_job.video_path.startswith("s3://") or db_job.video_path.startswith("cloudinary://"):
            return None
        candidates.append(Path(db_job.video_path))
    if db_job.out_dir:
        candidates.append(Path(db_job.out_dir) / "final.mp4")
    for path in candidates:
        resolved = _resolve_artifact_path(
            path,
            allowed_suffixes={".mp4", ".webm", ".mov"},
            out_dir=out_dir,
        )
        if resolved:
            return resolved
    return None


def _job_plan_path(db_job: JobModel) -> Optional[Path]:
    out_dir = Path(db_job.out_dir) if db_job.out_dir else None
    if db_job.plan_path:
        if db_job.plan_path.startswith("s3://") or db_job.plan_path.startswith("cloudinary://"):
            return None
        resolved = _resolve_artifact_path(
            Path(db_job.plan_path),
            allowed_suffixes={".json"},
            out_dir=out_dir,
        )
        if resolved:
            return resolved
    return None


def _job_log_path(db_job: JobModel) -> Optional[Path]:
    out_dir = Path(db_job.out_dir) if db_job.out_dir else None
    if db_job.log_path:
        if db_job.log_path.startswith("s3://") or db_job.log_path.startswith("cloudinary://"):
            return None
        resolved = _resolve_artifact_path(
            Path(db_job.log_path),
            allowed_suffixes={".txt", ".log"},
            out_dir=out_dir,
        )
        if resolved:
            return resolved
    if db_job.out_dir:
        resolved = _resolve_artifact_path(
            Path(db_job.out_dir) / "log.txt",
            allowed_suffixes={".txt", ".log"},
            out_dir=out_dir,
        )
        if resolved:
            return resolved
    return None


def _job_artifact_urls(db_job: JobModel) -> dict:
    urls = {
        "video_url": None,
        "plan_url": None,
        "log_url": None,
    }

    protected_video_url = f"/api/v1/jobs/{db_job.id}/video"
    if db_job.video_path and (db_job.video_path.startswith("s3://") or db_job.video_path.startswith("cloudinary://")):
        try:
            if cloud_storage:
                urls["video_url"] = cloud_storage.generate_signed_url(db_job.video_path, expires_in=3600)
            else:
                urls["video_url"] = protected_video_url
        except Exception:
            urls["video_url"] = protected_video_url
    elif _job_video_path(db_job):
        urls["video_url"] = protected_video_url

    protected_plan_url = f"/api/v1/jobs/{db_job.id}/plan"
    if db_job.plan_path and (db_job.plan_path.startswith("s3://") or db_job.plan_path.startswith("cloudinary://")):
        try:
            if cloud_storage:
                urls["plan_url"] = cloud_storage.generate_signed_url(db_job.plan_path, expires_in=3600)
            else:
                urls["plan_url"] = protected_plan_url
        except Exception:
            urls["plan_url"] = protected_plan_url
    elif _job_plan_path(db_job):
        urls["plan_url"] = protected_plan_url

    protected_log_url = f"/api/v1/jobs/{db_job.id}/log"
    if _job_log_path(db_job):
        urls["log_url"] = protected_log_url

    return urls


_WEBAUTHN_CHALLENGES: dict[str, datetime] = {}
_SOCIAL_AUTH_STATES: dict[str, dict] = {}
_WEBAUTHN_CHALLENGE_TTL_SECONDS = max(60, _env_int("WEBAUTHN_CHALLENGE_TTL_SECONDS", 600))
_WEBAUTHN_CHALLENGE_MAX_ENTRIES = max(100, _env_int("WEBAUTHN_CHALLENGE_MAX_ENTRIES", 10000))


def _tenant_context(request: Request, current_user: Optional[User] = None) -> str:
    if current_user and current_user.role == UserRole.ADMIN:
        return request.headers.get("X-Tenant-ID", "default").strip() or "default"
    return request.headers.get("X-Tenant-ID", "default").strip() or "default"


def _resolve_login_identifier_to_email(identifier: str) -> str:
    """Allow an admin ID alias while keeping email-based storage/auth."""
    normalized = (identifier or "").strip().lower()
    if "@" in normalized:
        return normalized

    admin_login_id = (os.getenv("ADMIN_LOGIN_ID", "admin") or "admin").strip().lower()
    admin_email = (os.getenv("ADMIN_EMAIL", "admin@phiversity.local") or "").strip().lower()
    if normalized and normalized == admin_login_id and admin_email:
        return admin_email

    return normalized


def _social_provider_config(provider: str) -> dict:
    provider = provider.strip().lower()
    if provider == "google":
        return {
            "provider": "google",
            "client_id": os.getenv("GOOGLE_CLIENT_ID", "").strip(),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", "").strip(),
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "").strip(),
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://openidconnect.googleapis.com/v1/userinfo",
            "scopes": "openid email profile",
        }
    if provider == "facebook":
        return {
            "provider": "facebook",
            "client_id": os.getenv("FACEBOOK_APP_ID", "").strip(),
            "client_secret": os.getenv("FACEBOOK_APP_SECRET", "").strip(),
            "redirect_uri": os.getenv("FACEBOOK_REDIRECT_URI", "").strip(),
            "authorize_url": "https://www.facebook.com/v20.0/dialog/oauth",
            "token_url": "https://graph.facebook.com/v20.0/oauth/access_token",
            "userinfo_url": "https://graph.facebook.com/me?fields=id,name,email",
            "scopes": "email,public_profile",
        }
    raise HTTPException(status_code=404, detail="Unsupported social provider")


def _prune_social_states() -> None:
    now = datetime.now(timezone.utc)
    to_remove = []
    for state, meta in _SOCIAL_AUTH_STATES.items():
        expires_at = meta.get("expires_at")
        if isinstance(expires_at, datetime) and expires_at <= now:
            to_remove.append(state)
    for state in to_remove:
        _SOCIAL_AUTH_STATES.pop(state, None)


def _prune_webauthn_challenges() -> None:
    now = datetime.now(timezone.utc)
    expired_keys: list[str] = []

    for key, expires_at in _WEBAUTHN_CHALLENGES.items():
        if not isinstance(expires_at, datetime):
            expired_keys.append(key)
            continue
        if expires_at <= now:
            expired_keys.append(key)

    for key in expired_keys:
        _WEBAUTHN_CHALLENGES.pop(key, None)

    overflow = len(_WEBAUTHN_CHALLENGES) - _WEBAUTHN_CHALLENGE_MAX_ENTRIES
    if overflow > 0:
        # Dict preserves insertion order in Python 3.7+, so remove oldest entries first.
        stale_keys = list(_WEBAUTHN_CHALLENGES.keys())[:overflow]
        for key in stale_keys:
            _WEBAUTHN_CHALLENGES.pop(key, None)


def _pkce_s256_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def _json_text_to_list(value: Optional[str]) -> List[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []

# --- Endpoints ---

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "ok", 
        "service": "phiversity-api", 
        "version": "1.1.0",
        "job_execution_mode": _job_execution_mode(),
        "schema_readiness_required": schema_readiness_required(),
        "timestamp": time.time()
    }


@app.get("/api/v1/system/llm-key-status", tags=["System"])
async def get_llm_key_status(current_user: User = Depends(get_current_user)):
    path = TEXTS_DIR / "llm_key_check.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Status file not found")
    return FileResponse(path, media_type="application/json", filename="llm_key_check.json")


@app.get("/api/v1/system/queue-health", tags=["System"])
async def get_queue_health(
    service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    return service.queue_metrics()


@app.get("/api/v1/admin/system/storage-health", tags=["Admin", "System"])
@limiter.limit("30/minute")
async def get_admin_storage_health(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Return storage backend state and a quick S3 connectivity check for admins."""
    _require_admin(current_user)

    backend = "unavailable"
    if cloud_storage is not None:
        backend = getattr(cloud_storage, "backend", "unknown")

    storage = {
        "backend": backend,
        "cloud_storage_loaded": cloud_storage is not None,
        "is_cloud_backend": backend in {"s3", "cloudinary"},
    }

    s3 = {
        "check_performed": False,
        "connected": None,
        "bucket_configured": bool(os.getenv("AWS_S3_BUCKET")),
        "latency_ms": None,
        "error": None,
    }

    if backend == "s3" and cloud_storage is not None:
        s3["check_performed"] = True
        bucket_name = getattr(cloud_storage, "bucket_name", None) or os.getenv("AWS_S3_BUCKET")
        s3["bucket_configured"] = bool(bucket_name)

        s3_client = getattr(cloud_storage, "s3_client", None)
        if not bucket_name:
            s3["connected"] = False
            s3["error"] = "AWS_S3_BUCKET is not configured"
        elif s3_client is None:
            s3["connected"] = False
            s3["error"] = "S3 client is not initialized"
        else:
            started = time.perf_counter()
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                s3["connected"] = True
            except Exception as exc:
                s3["connected"] = False
                s3["error"] = f"{exc.__class__.__name__}: {exc}"
            finally:
                s3["latency_ms"] = round((time.perf_counter() - started) * 1000.0, 2)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "storage": storage,
        "s3": s3,
    }


@app.get("/api/v1/admin/system/email-health", tags=["Admin", "System"])
@limiter.limit("30/minute")
async def get_admin_email_health(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    provider = (os.getenv("EMAIL_PROVIDER", "log").strip().lower() or "log")
    from_email = os.getenv("EMAIL_FROM", "").strip()
    required = {
        "sendgrid": ["SENDGRID_API_KEY", "EMAIL_FROM"],
        "mailgun": ["MAILGUN_API_KEY", "MAILGUN_DOMAIN", "EMAIL_FROM"],
        "ses": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION", "EMAIL_FROM"],
        "log": ["EMAIL_FROM"],
    }
    req_keys = required.get(provider, [])
    missing = [k for k in req_keys if not os.getenv(k, "").strip()]
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "configured": len(missing) == 0,
        "from_email": from_email,
        "missing_keys": missing,
    }


@app.get("/api/v1/auth/social/{provider}/start", tags=["Auth", "OAuth2"])
@limiter.limit("20/minute")
async def social_login_start(
    provider: str,
    request: Request,
    redirect_uri: Optional[str] = None,
):
    cfg = _social_provider_config(provider)
    if not cfg["client_id"]:
        raise HTTPException(status_code=503, detail=f"{provider} OAuth is not configured")

    _prune_social_states()
    state = secrets.token_urlsafe(24)
    target_redirect_uri = redirect_uri or cfg["redirect_uri"]
    if not target_redirect_uri:
        raise HTTPException(status_code=400, detail="redirect_uri is required")

    _SOCIAL_AUTH_STATES[state] = {
        "provider": provider.lower(),
        "redirect_uri": target_redirect_uri,
        "tenant_id": _tenant_context(request),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
    }

    params = {
        "client_id": cfg["client_id"],
        "redirect_uri": target_redirect_uri,
        "state": state,
        "response_type": "code",
        "scope": cfg["scopes"],
    }
    if provider.lower() == "google":
        params["access_type"] = "offline"
        params["prompt"] = "consent"

    logger.info(
        "Social auth started",
        extra={"provider": provider.lower(), "tenant_id": _tenant_context(request)},
    )

    return {
        "provider": provider.lower(),
        "state": state,
        "authorization_url": f"{cfg['authorize_url']}?{urlencode(params)}",
    }


@app.post("/api/v1/auth/social/{provider}/callback", response_model=Token, tags=["Auth", "OAuth2"])
@limiter.limit("30/minute")
async def social_login_callback(
    provider: str,
    request: Request,
    service: UserService = Depends(get_user_service),
):
    body = await request.json()
    code = str(body.get("code", "")).strip()
    state = str(body.get("state", "")).strip()
    email_hint = str(body.get("email_hint", "")).strip().lower() or None

    if not state:
        raise HTTPException(status_code=400, detail="Missing state")
    meta = _SOCIAL_AUTH_STATES.pop(state, None)
    if not meta:
        raise HTTPException(status_code=400, detail="Invalid or expired social state")
    if meta.get("provider") != provider.lower():
        raise HTTPException(status_code=400, detail="State/provider mismatch")

    cfg = _social_provider_config(provider)
    email = None

    if code and cfg["client_secret"]:
        try:
            token_resp = requests.post(
                cfg["token_url"],
                data={
                    "client_id": cfg["client_id"],
                    "client_secret": cfg["client_secret"],
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": meta.get("redirect_uri"),
                },
                timeout=10,
            )
            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if access_token:
                user_resp = requests.get(
                    cfg["userinfo_url"],
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10,
                )
                profile = user_resp.json()
                email = (profile.get("email") or "").strip().lower() or None
        except Exception:
            email = None

    allow_dev_hint = os.getenv("SOCIAL_AUTH_ALLOW_EMAIL_HINT_DEV", "false").lower() in {"1", "true", "yes"}
    if not email and allow_dev_hint and email_hint:
        email = email_hint

    if not email:
        raise HTTPException(status_code=400, detail="Could not resolve social account email")

    user = service.get_user_by_email(email)
    if not user:
        generated_password = secrets.token_urlsafe(32)
        user = service.create_user(email=email, password=generated_password)
    user.email_verified = True
    if not user.email_verified_at:
        user.email_verified_at = datetime.now(timezone.utc)
    service.db.commit()

    logger.info(
        "Social auth completed",
        extra={"provider": provider.lower(), "user_id": user.id, "tenant_id": meta.get("tenant_id", "default")},
    )

    issued = service.issue_session_tokens(
        user,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    response = JSONResponse(
        {
            "access_token": issued["access_token"],
            "refresh_token": issued["refresh_token"],
            "token_type": issued["token_type"],
        }
    )
    refresh_expires_at = issued.get("refresh_expires_at") or (datetime.now(timezone.utc) + timedelta(days=30))
    secure_cookies = os.getenv("PHIVERSITY_ENV") in {"prod", "production", "staging"}
    HttpOnlyCookieManager.set_refresh_token_cookie(
        response=response,
        token=issued["refresh_token"],
        expires_at=refresh_expires_at,
        secure=secure_cookies,
    )
    csrf_token = generate_csrf_token()
    HttpOnlyCookieManager.set_csrf_token_cookie(response=response, token=csrf_token, secure=secure_cookies)
    response.headers["X-CSRF-Token"] = csrf_token
    return response


@app.get("/api/v1/billing/tiers", tags=["Billing"])
@limiter.limit("60/minute")
async def get_billing_tiers(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    billing = BillingService()
    tiers = billing.get_tiers()
    tier_catalog = {
        tier: {
            "display_name": str((details or {}).get("display_name") or tier.title()),
            "badge": str((details or {}).get("badge") or ""),
            "summary": str((details or {}).get("summary") or ""),
            "amount_usd": int((details or {}).get("amount_usd", 0) or 0),
            "yearly_amount_usd": int((details or {}).get("yearly_amount_usd", 0) or 0),
            "features": list((details or {}).get("features") or []),
            "recommended": bool((details or {}).get("recommended", False)),
        }
        for tier, details in tiers.items()
    }
    recommended_tier = next(
        (tier for tier, details in tier_catalog.items() if details.get("recommended")),
        "premium" if "premium" in tier_catalog else (next(iter(tier_catalog.keys()), "free")),
    )

    return {
        "tiers": tiers,
        "tier_catalog": tier_catalog,
        "recommended_tier": recommended_tier,
        "currency": "USD",
        "current_tier": current_user.quality_tier.value,
        "tenant_id": _tenant_context(request, current_user),
        "providers": {
            "stripe": bool(os.getenv("STRIPE_PUBLISHABLE_KEY", "").strip()),
            "paypal": bool(os.getenv("PAYPAL_CLIENT_ID", "").strip()),
        },
    }


_ALLOWED_BILLING_TIERS = {tier.value for tier in QualityTier}
_STRIPE_UPGRADE_EVENTS = {"checkout.session.completed", "customer.subscription.updated", "invoice.paid"}
_STRIPE_DOWNGRADE_EVENTS = {"customer.subscription.deleted", "invoice.payment_failed"}
_PAYPAL_UPGRADE_EVENTS = {"BILLING.SUBSCRIPTION.ACTIVATED", "PAYMENT.SALE.COMPLETED"}
_PAYPAL_DOWNGRADE_EVENTS = {"BILLING.SUBSCRIPTION.CANCELLED", "BILLING.SUBSCRIPTION.SUSPENDED"}


def _parse_int_user_id(raw_user_id: Optional[str]) -> Optional[int]:
    try:
        return int(raw_user_id) if raw_user_id is not None else None
    except (TypeError, ValueError):
        return None


def _normalize_billing_tier(raw_tier: Optional[str]) -> Optional[str]:
    candidate = str(raw_tier or "").strip().lower()
    return candidate if candidate in _ALLOWED_BILLING_TIERS else None


def _safe_json_dumps(payload: Any) -> str:
    try:
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=True, sort_keys=True)
    except Exception:
        return "{}"


def _parse_event_datetime(raw_value: Any) -> Optional[datetime]:
    if raw_value is None:
        return None
    if isinstance(raw_value, (int, float)):
        try:
            return datetime.fromtimestamp(float(raw_value), tz=timezone.utc)
        except Exception:
            return None
    if isinstance(raw_value, str):
        candidate = raw_value.strip()
        if not candidate:
            return None
        if candidate.isdigit():
            try:
                return datetime.fromtimestamp(float(candidate), tz=timezone.utc)
            except Exception:
                return None
        if candidate.endswith("Z"):
            candidate = candidate[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            return None
    return None


def _parse_paypal_amount_to_cents(raw_value: Any) -> int:
    if raw_value is None:
        return 0
    if isinstance(raw_value, (int, float)):
        return int(Decimal(str(raw_value)) * 100)
    if isinstance(raw_value, str):
        candidate = raw_value.strip()
        if not candidate:
            return 0
        try:
            return int(Decimal(candidate) * 100)
        except (InvalidOperation, ValueError):
            return 0
    if isinstance(raw_value, dict):
        return _parse_paypal_amount_to_cents(raw_value.get("value") or raw_value.get("total"))
    return 0


def _extract_custom_id_parts(custom_id: Any) -> dict[str, str]:
    if not isinstance(custom_id, str) or not custom_id.strip():
        return {}
    parts: dict[str, str] = {}
    for piece in custom_id.split(";"):
        if "=" not in piece:
            continue
        k, v = piece.split("=", 1)
        key = k.strip()
        value = v.strip()
        if key:
            parts[key] = value
    return parts


def _normalize_subscription_status(raw_status: Any) -> str:
    value = str(raw_status or "").strip().lower()
    status_map = {
        "active": "active",
        "trialing": "trialing",
        "past_due": "past_due",
        "past due": "past_due",
        "suspended": "past_due",
        "cancelled": "canceled",
        "canceled": "canceled",
        "inactive": "canceled",
    }
    return status_map.get(value, value or "active")


def _normalize_invoice_status(raw_status: Any) -> str:
    value = str(raw_status or "").strip().lower()
    status_map = {
        "draft": "open",
        "open": "open",
        "paid": "paid",
        "void": "void",
        "voided": "void",
        "uncollectible": "uncollectible",
    }
    return status_map.get(value, value or "open")


def _normalize_transaction_status(event_type: str, raw_status: Any) -> str:
    value = str(raw_status or "").strip().lower()
    if value in {"succeeded", "completed", "paid", "success"}:
        return "succeeded"
    if value in {"pending", "in_progress", "processing"}:
        return "pending"
    if value in {"failed", "denied", "declined"}:
        return "failed"
    if value in {"refunded", "refund"}:
        return "refunded"

    event_lower = (event_type or "").lower()
    if "refund" in event_lower:
        return "refunded"
    if "failed" in event_lower or "denied" in event_lower:
        return "failed"
    if "pending" in event_lower or "review" in event_lower:
        return "pending"
    return "succeeded"


def _upsert_payment_account(
    *,
    db: Session,
    user_id: int,
    provider: str,
    provider_customer_id: Optional[str],
    email: Optional[str],
    default_payment_method: Optional[str],
) -> Optional[PaymentAccount]:
    customer_id = str(provider_customer_id or "").strip()
    if not customer_id:
        return None

    account = (
        db.query(PaymentAccount)
        .filter(
            PaymentAccount.provider == provider,
            PaymentAccount.provider_customer_id == customer_id,
        )
        .first()
    )
    if not account:
        account = PaymentAccount(
            user_id=user_id,
            provider=provider,
            provider_customer_id=customer_id,
        )
        db.add(account)

    account.user_id = user_id
    account.is_active = True
    if email:
        account.email = str(email).strip().lower()
    if default_payment_method:
        account.default_payment_method = str(default_payment_method).strip()
    return account


def _upsert_subscription(
    *,
    db: Session,
    user_id: int,
    provider: str,
    provider_subscription_id: Optional[str],
    tier: Optional[str],
    status: Optional[str],
    currency: Optional[str],
    amount_cents: Optional[int],
    interval: Optional[str],
    period_start: Optional[datetime],
    period_end: Optional[datetime],
    cancel_at_period_end: Optional[bool],
    tenant_id: Optional[str],
    payment_account: Optional[PaymentAccount],
    metadata: Any,
) -> Optional[Subscription]:
    subscription_id = str(provider_subscription_id or "").strip()
    if not subscription_id:
        return None

    record = (
        db.query(Subscription)
        .filter(
            Subscription.provider == provider,
            Subscription.provider_subscription_id == subscription_id,
        )
        .first()
    )
    if not record:
        record = Subscription(
            user_id=user_id,
            provider=provider,
            provider_subscription_id=subscription_id,
            tier=tier or QualityTier.FREE.value,
        )
        db.add(record)

    record.user_id = user_id
    record.payment_account_id = payment_account.id if payment_account else None
    if tier:
        record.tier = tier
    record.status = _normalize_subscription_status(status)
    if currency:
        record.currency = str(currency).upper()
    if amount_cents is not None:
        record.amount_cents = max(0, int(amount_cents))
    if interval:
        record.interval = str(interval).strip().lower()
    record.period_start = period_start
    record.period_end = period_end
    if cancel_at_period_end is not None:
        record.cancel_at_period_end = bool(cancel_at_period_end)
    record.tenant_id = tenant_id
    record.metadata_json = _safe_json_dumps(metadata)
    return record


def _upsert_invoice(
    *,
    db: Session,
    user_id: int,
    provider: str,
    provider_invoice_id: Optional[str],
    subscription: Optional[Subscription],
    status: Optional[str],
    amount_due_cents: Optional[int],
    amount_paid_cents: Optional[int],
    currency: Optional[str],
    hosted_invoice_url: Optional[str],
    invoice_pdf_url: Optional[str],
    due_at: Optional[datetime],
    paid_at: Optional[datetime],
    metadata: Any,
) -> Optional[PaymentInvoice]:
    invoice_id = str(provider_invoice_id or "").strip()
    if not invoice_id:
        return None

    record = (
        db.query(PaymentInvoice)
        .filter(
            PaymentInvoice.provider == provider,
            PaymentInvoice.provider_invoice_id == invoice_id,
        )
        .first()
    )
    if not record:
        record = PaymentInvoice(
            user_id=user_id,
            provider=provider,
            provider_invoice_id=invoice_id,
        )
        db.add(record)

    record.user_id = user_id
    record.subscription_id = subscription.id if subscription else None
    record.status = _normalize_invoice_status(status)
    if amount_due_cents is not None:
        record.amount_due_cents = max(0, int(amount_due_cents))
    if amount_paid_cents is not None:
        record.amount_paid_cents = max(0, int(amount_paid_cents))
    if currency:
        record.currency = str(currency).upper()
    record.hosted_invoice_url = hosted_invoice_url
    record.invoice_pdf_url = invoice_pdf_url
    record.due_at = due_at
    record.paid_at = paid_at
    record.metadata_json = _safe_json_dumps(metadata)
    return record


def _upsert_transaction(
    *,
    db: Session,
    user_id: int,
    provider: str,
    provider_payment_id: Optional[str],
    event_type: str,
    status: Optional[str],
    amount_cents: Optional[int],
    currency: Optional[str],
    payment_method: Optional[str],
    failure_code: Optional[str],
    failure_message: Optional[str],
    occurred_at: Optional[datetime],
    subscription: Optional[Subscription],
    invoice: Optional[PaymentInvoice],
    metadata: Any,
) -> Optional[PaymentTransaction]:
    payment_id = str(provider_payment_id or "").strip()
    if not payment_id:
        return None

    record = (
        db.query(PaymentTransaction)
        .filter(
            PaymentTransaction.provider == provider,
            PaymentTransaction.provider_payment_id == payment_id,
        )
        .first()
    )
    if not record:
        record = PaymentTransaction(
            user_id=user_id,
            provider=provider,
            provider_payment_id=payment_id,
        )
        db.add(record)

    record.user_id = user_id
    record.subscription_id = subscription.id if subscription else None
    record.invoice_id = invoice.id if invoice else None
    record.event_type = event_type
    record.status = _normalize_transaction_status(event_type, status)
    if amount_cents is not None:
        record.amount_cents = max(0, int(amount_cents))
    if currency:
        record.currency = str(currency).upper()
    record.payment_method = payment_method
    record.failure_code = failure_code
    record.failure_message = failure_message
    record.occurred_at = occurred_at
    record.metadata_json = _safe_json_dumps(metadata)
    return record


def _persist_stripe_billing_event(
    *,
    db: Session,
    event_type: str,
    event: dict[str, Any],
) -> bool:
    obj = ((event.get("data") or {}).get("object") or {})
    metadata = obj.get("metadata") or {}
    user_id = _parse_int_user_id(metadata.get("user_id") or obj.get("client_reference_id"))
    if user_id is None:
        return False

    user_exists = db.query(User.id).filter(User.id == user_id).first()
    if not user_exists:
        return False

    tier = _normalize_billing_tier(metadata.get("tier"))
    tenant_id = str(metadata.get("tenant_id") or "").strip() or None

    customer_id = obj.get("customer") or metadata.get("customer_id")
    customer_email = obj.get("customer_email") or (obj.get("customer_details") or {}).get("email") or obj.get("email")
    default_payment_method = obj.get("default_payment_method") or obj.get("payment_method")
    account = _upsert_payment_account(
        db=db,
        user_id=user_id,
        provider="stripe",
        provider_customer_id=customer_id,
        email=customer_email,
        default_payment_method=default_payment_method,
    )
    if account and account.id is None:
        db.flush()

    subscription_id = (
        obj.get("subscription")
        or (obj.get("id") if event_type.startswith("customer.subscription.") else None)
        or metadata.get("subscription_id")
    )
    items = (obj.get("items") or {}).get("data") or []
    first_item = items[0] if isinstance(items, list) and items else {}
    recurring = ((first_item.get("price") or {}).get("recurring") or {}) if isinstance(first_item, dict) else {}
    interval = recurring.get("interval") or metadata.get("interval")
    amount_cents = (
        obj.get("amount_total")
        or obj.get("amount_due")
        or obj.get("amount_paid")
        or ((obj.get("plan") or {}).get("amount"))
    )
    subscription = _upsert_subscription(
        db=db,
        user_id=user_id,
        provider="stripe",
        provider_subscription_id=subscription_id,
        tier=tier,
        status=obj.get("status"),
        currency=obj.get("currency"),
        amount_cents=int(amount_cents) if amount_cents is not None else None,
        interval=interval,
        period_start=_parse_event_datetime(obj.get("current_period_start")),
        period_end=_parse_event_datetime(obj.get("current_period_end")),
        cancel_at_period_end=obj.get("cancel_at_period_end"),
        tenant_id=tenant_id,
        payment_account=account,
        metadata=obj,
    )

    db.flush()

    invoice_id = obj.get("invoice") or (obj.get("id") if event_type.startswith("invoice.") else None)
    invoice = _upsert_invoice(
        db=db,
        user_id=user_id,
        provider="stripe",
        provider_invoice_id=invoice_id,
        subscription=subscription,
        status=obj.get("status"),
        amount_due_cents=int(obj.get("amount_due")) if obj.get("amount_due") is not None else None,
        amount_paid_cents=int(obj.get("amount_paid")) if obj.get("amount_paid") is not None else None,
        currency=obj.get("currency"),
        hosted_invoice_url=obj.get("hosted_invoice_url"),
        invoice_pdf_url=obj.get("invoice_pdf"),
        due_at=_parse_event_datetime(obj.get("due_date")),
        paid_at=_parse_event_datetime(((obj.get("status_transitions") or {}).get("paid_at")) or obj.get("paid_at")),
        metadata=obj,
    )

    db.flush()

    payment_id = (
        obj.get("payment_intent")
        or obj.get("charge")
        or obj.get("id")
        or obj.get("invoice")
    )
    payment_method_details = obj.get("payment_method_details") or {}
    payment_method = obj.get("payment_method") or payment_method_details.get("type")
    transaction_amount = (
        obj.get("amount_total")
        or obj.get("amount_paid")
        or obj.get("amount_received")
        or obj.get("amount")
        or obj.get("amount_due")
    )

    transaction = _upsert_transaction(
        db=db,
        user_id=user_id,
        provider="stripe",
        provider_payment_id=payment_id,
        event_type=event_type,
        status=obj.get("status"),
        amount_cents=int(transaction_amount) if transaction_amount is not None else None,
        currency=obj.get("currency"),
        payment_method=payment_method,
        failure_code=obj.get("failure_code") or obj.get("failure_reason"),
        failure_message=obj.get("failure_message") or obj.get("decline_code"),
        occurred_at=_parse_event_datetime(obj.get("created")),
        subscription=subscription,
        invoice=invoice,
        metadata=obj,
    )

    db.commit()
    return any([account, subscription, invoice, transaction])


def _persist_paypal_billing_event(
    *,
    db: Session,
    event_type: str,
    event: dict[str, Any],
) -> bool:
    resource = event.get("resource") or {}
    custom_parts = _extract_custom_id_parts(resource.get("custom_id"))
    user_id = _parse_int_user_id(custom_parts.get("user_id"))
    if user_id is None:
        return False

    user_exists = db.query(User.id).filter(User.id == user_id).first()
    if not user_exists:
        return False

    tier = _normalize_billing_tier(custom_parts.get("tier"))
    tenant_id = custom_parts.get("tenant_id")

    payer = resource.get("payer") or {}
    subscriber = resource.get("subscriber") or {}
    provider_customer_id = (
        payer.get("payer_id")
        or subscriber.get("payer_id")
        or custom_parts.get("payer_id")
    )
    payer_email = payer.get("email_address") or subscriber.get("email_address")
    account = _upsert_payment_account(
        db=db,
        user_id=user_id,
        provider="paypal",
        provider_customer_id=provider_customer_id,
        email=payer_email,
        default_payment_method=(resource.get("payment_source") or {}).get("type"),
    )
    if account and account.id is None:
        db.flush()

    related_ids = ((resource.get("supplementary_data") or {}).get("related_ids") or {})
    subscription_id = (
        (resource.get("id") if event_type.startswith("BILLING.SUBSCRIPTION.") else None)
        or resource.get("billing_agreement_id")
        or related_ids.get("subscription_id")
        or custom_parts.get("subscription_id")
    )
    billing_info = resource.get("billing_info") or {}
    subscription = _upsert_subscription(
        db=db,
        user_id=user_id,
        provider="paypal",
        provider_subscription_id=subscription_id,
        tier=tier,
        status=resource.get("status") or resource.get("state"),
        currency=(resource.get("amount") or {}).get("currency_code") or (resource.get("amount") or {}).get("currency"),
        amount_cents=_parse_paypal_amount_to_cents(resource.get("amount")),
        interval=custom_parts.get("interval") or "month",
        period_start=_parse_event_datetime(resource.get("start_time")),
        period_end=_parse_event_datetime(billing_info.get("next_billing_time")),
        cancel_at_period_end=False,
        tenant_id=tenant_id,
        payment_account=account,
        metadata=resource,
    )

    db.flush()

    invoice_id = resource.get("invoice_id") or resource.get("invoice_number") or related_ids.get("order_id")
    invoice = _upsert_invoice(
        db=db,
        user_id=user_id,
        provider="paypal",
        provider_invoice_id=invoice_id,
        subscription=subscription,
        status=resource.get("status") or resource.get("state"),
        amount_due_cents=_parse_paypal_amount_to_cents(resource.get("amount")),
        amount_paid_cents=_parse_paypal_amount_to_cents(resource.get("amount")),
        currency=(resource.get("amount") or {}).get("currency_code") or (resource.get("amount") or {}).get("currency"),
        hosted_invoice_url=resource.get("href"),
        invoice_pdf_url=None,
        due_at=_parse_event_datetime(resource.get("next_payment_date")),
        paid_at=_parse_event_datetime(resource.get("create_time") or resource.get("update_time")),
        metadata=resource,
    )

    db.flush()

    payment_id = resource.get("id") or related_ids.get("capture_id") or related_ids.get("order_id")
    transaction = _upsert_transaction(
        db=db,
        user_id=user_id,
        provider="paypal",
        provider_payment_id=payment_id,
        event_type=event_type,
        status=resource.get("status") or resource.get("state"),
        amount_cents=_parse_paypal_amount_to_cents(resource.get("amount")),
        currency=(resource.get("amount") or {}).get("currency_code") or (resource.get("amount") or {}).get("currency"),
        payment_method=(resource.get("payment_mode") or (resource.get("payment_source") or {}).get("type")),
        failure_code=resource.get("reason_code"),
        failure_message=resource.get("reason") or resource.get("status_details"),
        occurred_at=_parse_event_datetime(resource.get("create_time") or resource.get("update_time") or event.get("create_time")),
        subscription=subscription,
        invoice=invoice,
        metadata=resource,
    )

    db.commit()
    return any([account, subscription, invoice, transaction])


def _sync_user_tier_from_billing_event(
    *,
    service: UserService,
    provider: str,
    event_type: str,
    raw_user_id: Optional[str],
    raw_tier: Optional[str],
    upgrade_events: set[str],
    downgrade_events: set[str],
) -> tuple[bool, Optional[str], Optional[int]]:
    user_id = _parse_int_user_id(raw_user_id)
    if user_id is None:
        return False, None, None

    desired_tier: Optional[str] = None
    if event_type in upgrade_events:
        desired_tier = _normalize_billing_tier(raw_tier)
    elif event_type in downgrade_events:
        desired_tier = QualityTier.FREE.value

    if not desired_tier:
        return False, None, user_id

    user = service.db.query(User).filter(User.id == user_id).first()
    if not user:
        return False, desired_tier, user_id

    if user.quality_tier.value != desired_tier:
        user.quality_tier = QualityTier(desired_tier)
        service.db.commit()

    NotificationService().send_payment_confirmation_email(user.email, tier=desired_tier, provider=provider)
    return True, desired_tier, user_id


@app.post("/api/v1/billing/checkout", tags=["Billing"])
@limiter.limit("20/minute")
async def create_billing_checkout(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    body = await request.json()
    provider = str(body.get("provider", "")).strip().lower()
    tier = str(body.get("tier", "")).strip().lower()
    success_url = str(body.get("success_url", "")).strip() or str(request.base_url)
    cancel_url = str(body.get("cancel_url", "")).strip() or str(request.base_url)
    billing = BillingService()
    tiers = billing.get_tiers()
    if tier not in tiers:
        raise HTTPException(status_code=400, detail="Unknown subscription tier")

    try:
        checkout = billing.create_checkout(
            provider=provider,
            tier=tier,
            user_id=current_user.id,
            tenant_id=_tenant_context(request, current_user),
            success_url=success_url,
            cancel_url=cancel_url,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    logger.info(
        "Billing checkout created",
        extra={
            "provider": checkout["provider"],
            "tier": tier,
            "user_id": current_user.id,
            "tenant_id": _tenant_context(request, current_user),
            "session_ref": checkout["session_ref"],
        },
    )

    return {
        "provider": checkout["provider"],
        "tier": tier,
        "checkout_url": checkout["checkout_url"],
        "session_ref": checkout["session_ref"],
    }


@app.get("/api/v1/billing/portal", tags=["Billing"])
@limiter.limit("30/minute")
async def get_billing_portal(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    billing = BillingService()
    url = billing.portal_url(current_user.id, _tenant_context(request, current_user))
    if not url:
        raise HTTPException(status_code=404, detail="Billing portal is not configured")
    return {"portal_url": url}


@app.post("/api/v1/billing/webhooks/stripe", tags=["Billing"])
@limiter.limit("240/minute")
async def stripe_webhook(request: Request, service: UserService = Depends(get_user_service)):
    billing = BillingService()
    raw_payload = await request.body()
    signature = request.headers.get("Stripe-Signature")
    if not billing.verify_stripe_signature(raw_payload, signature):
        raise HTTPException(status_code=401, detail="Invalid Stripe signature")

    event = json.loads(raw_payload.decode("utf-8"))
    event_type = event.get("type", "")
    obj = ((event.get("data") or {}).get("object") or {})
    metadata = obj.get("metadata") or {}
    user_id = metadata.get("user_id") or obj.get("client_reference_id")
    tier = metadata.get("tier")

    sync_applied, synchronized_tier, parsed_user_id = _sync_user_tier_from_billing_event(
        service=service,
        provider="stripe",
        event_type=event_type,
        raw_user_id=user_id,
        raw_tier=tier,
        upgrade_events=_STRIPE_UPGRADE_EVENTS,
        downgrade_events=_STRIPE_DOWNGRADE_EVENTS,
    )

    try:
        persistence_applied = _persist_stripe_billing_event(
            db=service.db,
            event_type=event_type,
            event=event,
        )
    except Exception:
        service.db.rollback()
        logger.exception("Stripe webhook persistence failed", extra={"event_type": event_type})
        raise HTTPException(status_code=500, detail="Failed to persist Stripe billing event")

    logger.info(
        "Stripe webhook received",
        extra={
            "event_type": event_type,
            "user_id": parsed_user_id,
            "tier": synchronized_tier,
            "sync_applied": sync_applied,
            "persistence_applied": persistence_applied,
        },
    )

    return {
        "received": True,
        "event_type": event_type,
        "sync_applied": sync_applied,
        "tier": synchronized_tier,
        "persistence_applied": persistence_applied,
    }


@app.post("/api/v1/billing/webhooks/paypal", tags=["Billing"])
@limiter.limit("240/minute")
async def paypal_webhook(request: Request, service: UserService = Depends(get_user_service)):
    billing = BillingService()
    raw_payload = await request.body()
    signature = request.headers.get("PayPal-Transmission-Sig")
    if not billing.verify_paypal_signature(signature, raw_payload):
        raise HTTPException(status_code=401, detail="Invalid PayPal signature")

    event = json.loads(raw_payload.decode("utf-8"))
    event_type = event.get("event_type", "")
    resource = event.get("resource") or {}
    custom = resource.get("custom_id", "")
    user_id = None
    tier = None
    if isinstance(custom, str) and custom:
        parts = dict(
            p.split("=", 1) for p in custom.split(";") if "=" in p
        )
        user_id = parts.get("user_id")
        tier = parts.get("tier")

    sync_applied, synchronized_tier, parsed_user_id = _sync_user_tier_from_billing_event(
        service=service,
        provider="paypal",
        event_type=event_type,
        raw_user_id=user_id,
        raw_tier=tier,
        upgrade_events=_PAYPAL_UPGRADE_EVENTS,
        downgrade_events=_PAYPAL_DOWNGRADE_EVENTS,
    )

    try:
        persistence_applied = _persist_paypal_billing_event(
            db=service.db,
            event_type=event_type,
            event=event,
        )
    except Exception:
        service.db.rollback()
        logger.exception("PayPal webhook persistence failed", extra={"event_type": event_type})
        raise HTTPException(status_code=500, detail="Failed to persist PayPal billing event")

    logger.info(
        "PayPal webhook received",
        extra={
            "event_type": event_type,
            "user_id": parsed_user_id,
            "tier": synchronized_tier,
            "sync_applied": sync_applied,
            "persistence_applied": persistence_applied,
        },
    )

    return {
        "received": True,
        "event_type": event_type,
        "sync_applied": sync_applied,
        "tier": synchronized_tier,
        "persistence_applied": persistence_applied,
    }


@app.get("/api/v1/admin/system/diagnostics", tags=["Admin", "System"])
@limiter.limit("20/minute")
async def get_admin_system_diagnostics(
    request: Request,
    include_sensitive: bool = False,
    service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user),
):
    """Return consolidated system diagnostics for admins only.

    By default, returns a redacted minimal-safe payload for production monitoring.
    Set include_sensitive=true to include operationally sensitive diagnostics details.
    """
    _require_admin(current_user)

    missing_schema = missing_required_schema(engine)
    queue = service.queue_metrics()

    keyring = JWTKeyRing()
    key_auth = {
        "secret_key_configured": bool(os.getenv("SECRET_KEY")),
        "jwt_algorithm": "HS256",
        "oauth2_token_url": "api/v1/auth/token",
        "csrf_enabled": True,
        "secure_cookies": os.getenv("PHIVERSITY_ENV") in {"prod", "production", "staging"},
    }

    if include_sensitive:
        key_auth.update(
            {
                "jwt_keyring_path": os.getenv("JWT_KEYRING_PATH", ".jwt_keyring.json"),
                "jwt_current_kid": keyring.get_current_key_id(),
                "jwt_valid_key_count": len(keyring.get_all_valid_keys()),
                "jwt_rotation": keyring.get_key_rotation_schedule(),
                "csrf_cookie_name": HttpOnlyCookieManager.CSRF_TOKEN_COOKIE,
                "csrf_header_name": CSRFProtection.CSRF_HEADER_NAME,
                "csrf_protected_paths": list(CSRF_PROTECTED_PATHS),
                "refresh_cookie_name": HttpOnlyCookieManager.REFRESH_TOKEN_COOKIE,
            }
        )

    database = {
        "schema_readiness_required": schema_readiness_required(),
        "schema_ready": len(missing_schema) == 0,
        "missing_schema_count": len(missing_schema),
    }
    if include_sensitive:
        database["missing_schema_items"] = missing_schema

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "include_sensitive": include_sensitive,
        "database": database,
        "queue": queue,
        "key_auth": key_auth,
    }


@app.get("/api/v1/admin/signup-profiles", tags=["Admin", "Auth"])
@limiter.limit("60/minute")
async def list_signup_profiles(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return signup profile records for admin inspection."""
    _require_admin(current_user)

    limit = max(1, min(int(limit), 200))
    offset = max(0, int(offset))

    base_query = db.query(UserProfile, User).join(User, User.id == UserProfile.user_id)
    total = base_query.count()
    rows = (
        base_query
        .order_by(UserProfile.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    profiles = []
    for profile, user in rows:
        profiles.append(
            {
                "user_id": user.id,
                "email": user.email,
                "username": profile.username,
                "signup_source": profile.signup_source,
                "signup_ip": profile.signup_ip,
                "signup_user_agent": profile.signup_user_agent,
                "created_at": profile.created_at.isoformat() if profile.created_at else None,
            }
        )

    return {
        "total": total,
        "count": len(profiles),
        "limit": limit,
        "offset": offset,
        "profiles": profiles,
    }

# --- Authentication ---

@app.post("/api/v1/auth/signup", response_model=UserResponse, tags=["Auth"])
@limiter.limit("10/minute")
async def signup(
    request: Request,
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService())
):
    # Validate password strength
    try:
        validate_password_strength(user_data.password)
    except ValueError as e:
        # Log failed signup attempt - weak password
        audit_service.log_event(
            db=service.db,
            event_type="signup",
            status="failure",
            description="Signup validation failed - weak password",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/signup",
            request_method="POST",
            response_status=400,
            error_message=str(e),
            metadata={"email": user_data.email[:3] + "***", "reason": "weak_password"}
        )
        raise HTTPException(status_code=400, detail=str(e))
    
    if service.get_user_by_email(user_data.email):
        # Log failed signup attempt - email already registered
        audit_service.log_event(
            db=service.db,
            event_type="signup",
            status="failure",
            description="Email already registered",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/signup",
            request_method="POST",
            response_status=400,
            error_message="Email already registered",
            metadata={"email": user_data.email[:3] + "***"}  # Partial obfuscation
        )
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        user = service.create_user(
            user_data.email,
            user_data.password,
            username=user_data.username,
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            signup_source=user_data.signup_source or "email",
            signup_ip=request.client.host if request.client else None,
            signup_user_agent=request.headers.get("user-agent"),
        )
        # Log successful signup
        audit_service.log_event(
            db=service.db,
            event_type="signup",
            status="success",
            user_id=user.id,
            description=f"User signed up",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/signup",
            request_method="POST",
            response_status=200,
        )
        return user
    except ValueError as e:
        # Log failed signup attempt - ValueError (email uniqueness)
        audit_service.log_event(
            db=service.db,
            event_type="signup",
            status="failure",
            description="Signup validation failed",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/signup",
            request_method="POST",
            response_status=400,
            error_message=str(e),
            metadata={"email": user_data.email[:3] + "***"}
        )
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/auth/token", response_model=Token, tags=["Auth"])
@limiter.limit("15/minute")
async def login(
    request: Request,
    login_data: LoginRequest,
    service: UserService = Depends(get_user_service),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService())
):
    login_email = _resolve_login_identifier_to_email(login_data.email)

    # Check if account is locked (configurable max attempts and lockout window)
    max_failed_attempts = int(os.getenv("AUTH_MAX_FAILED_ATTEMPTS", "5"))
    lockout_window_minutes = int(os.getenv("AUTH_LOCKOUT_WINDOW_MINUTES", "15"))
    
    if service.is_account_locked(
        login_email,
        max_attempts=max_failed_attempts,
        lockout_minutes=lockout_window_minutes,
    ):
        # Account is locked temporarily
        audit_service.log_event(
            db=service.db,
            event_type="login",
            status="failure",
            description="Login attempt blocked - account locked",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/token",
            request_method="POST",
            response_status=429,
            error_message="Account temporarily locked due to too many failed login attempts",
            metadata={"email": login_data.email[:3] + "***", "reason": "lockout"}
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked due to too many failed login attempts. Please try again later.",
        )

    user = service.authenticate_user(login_email, login_data.password)
    if not user:
        # Record failed attempt
        service.record_login_attempt(
            email=login_email,
            success=False,
            user_id=None,  # We don't know the user_id since login failed
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        # Log failed login attempt
        audit_service.log_event(
            db=service.db,
            event_type="login",
            status="failure",
            description="Failed authentication attempt",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/token",
            request_method="POST",
            response_status=401,
            error_message="Incorrect email or password",
            metadata={"email": login_data.email[:3] + "***"}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Optional MFA challenge when enabled on account.
    if user.mfa_enabled:
        mfa_code = request.headers.get("X-MFA-Code")
        backup_code = request.headers.get("X-MFA-Backup-Code")
        mfa_service = MFAService()
        secret = ""
        if user.mfa_secret_encrypted:
            try:
                secret = mfa_service.decrypt_secret(user.mfa_secret_encrypted)
            except Exception:
                secret = ""

        valid_mfa = bool(secret and mfa_code and mfa_service.verify_totp(secret, mfa_code))
        if not valid_mfa and backup_code and user.mfa_backup_codes_encrypted:
            hashes = mfa_service.decode_backup_hashes(user.mfa_backup_codes_encrypted)
            backup_hash = mfa_service.hash_backup_code(backup_code.upper())
            if backup_hash in hashes:
                hashes.remove(backup_hash)
                user.mfa_backup_codes_encrypted = mfa_service.encode_backup_hashes(hashes)
                service.db.commit()
                valid_mfa = True

        if not valid_mfa:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="MFA code required or invalid",
            )
    
    # Successful login - record it and clear any failed attempts
    service.record_login_attempt(
        email=login_email,
        success=True,
        user_id=user.id,
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # Geo-location anomaly baseline: detect IP changes and log high-severity event.
    current_ip = request.client.host if request.client else None
    if user.last_login_ip and current_ip and user.last_login_ip != current_ip:
        SecurityEventService(service.db).create_event(
            event_type="geo_ip_anomaly",
            severity="high",
            user_id=user.id,
            source="auth.login",
            description="Login detected from a new IP address",
            client_ip=current_ip,
            metadata={"previous_ip": user.last_login_ip, "current_ip": current_ip},
        )

    user.last_login_ip = current_ip
    user.last_login_at = datetime.now(timezone.utc)
    service.db.commit()
    
    issued = service.issue_session_tokens(
        user,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    # Log successful login
    audit_service.log_event(
        db=service.db,
        event_type="login",
        status="success",
        user_id=user.id,
        description="User authenticated successfully",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path="/api/v1/auth/token",
        request_method="POST",
        response_status=200,
    )
    response = JSONResponse(
        {
            "access_token": issued["access_token"],
            "refresh_token": issued["refresh_token"],
            "token_type": issued["token_type"],
        }
    )
    refresh_expires_at = issued.get("refresh_expires_at")
    if not refresh_expires_at:
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    HttpOnlyCookieManager.set_refresh_token_cookie(
        response=response,
        token=issued["refresh_token"],
        expires_at=refresh_expires_at,
        secure=os.getenv("PHIVERSITY_ENV") in {"prod", "production", "staging"},
    )
    csrf_token = generate_csrf_token()
    HttpOnlyCookieManager.set_csrf_token_cookie(
        response=response,
        token=csrf_token,
        secure=os.getenv("PHIVERSITY_ENV") in {"prod", "production", "staging"},
    )
    response.headers["X-CSRF-Token"] = csrf_token
    return response

@app.get("/api/v1/auth/me", response_model=UserResponse, tags=["Auth"])
async def read_users_me(request: Request, current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/api/v1/auth/export", tags=["Auth"])
async def export_user_data(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Export all user data in JSON format (GDPR compliance)."""
    # Get all jobs for this user
    jobs = service.db.query(JobModel).filter(JobModel.user_id == current_user.id).all()
    
    # Build export data
    export_data = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            "quality_tier": current_user.quality_tier.value if hasattr(current_user.quality_tier, 'value') else str(current_user.quality_tier),
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        },
        "jobs": [
            {
                "id": job.id,
                "status": job.status,
                "progress": job.progress,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "updated_at": job.updated_at.isoformat() if job.updated_at else None,
                "has_video": bool(job.video_path),
                "has_plan": bool(job.plan_path),
            }
            for job in jobs
        ],
        "jobs_count": len(jobs),
    }
    
    return export_data


@app.delete("/api/v1/auth/account", tags=["Auth"])
async def delete_user_account(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service),
    user_service: UserService = Depends(get_user_service)
):
    """Delete user account and all associated data (GDPR compliance)."""
    # Delete all jobs for this user
    jobs = service.db.query(JobModel).filter(JobModel.user_id == current_user.id).all()
    for job in jobs:
        # Delete associated files
        if job.out_dir:
            import shutil
            with suppress(Exception):
                shutil.rmtree(job.out_dir, ignore_errors=True)
        service.db.delete(job)
    
    # Delete the user
    service.db.delete(current_user)
    service.db.commit()
    
    logger.info(
        "User account deleted",
        extra={"user_id": current_user.id, "email_masked": _mask_email(current_user.email)},
    )
    return {"message": "Account and all associated data deleted successfully"}

@app.post("/api/v1/auth/guest", response_model=Token, tags=["Auth"])
@limiter.limit("10/minute")
async def guest_login(
    request: Request,
    service: UserService = Depends(get_user_service),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService())
):
    """Create or retrieve a guest account and return a JWT token."""
    import secrets
    from sqlalchemy.exc import IntegrityError, SQLAlchemyError

    user = None

    # Prefer per-session random guests to avoid cross-user coupling.
    for _ in range(5):
        guest_email = f"guest_{secrets.token_hex(8)}@guest.local"
        guest_password = secrets.token_hex(16)
        try:
            user = service.create_user(guest_email, guest_password)
            break
        except ValueError:
            service.db.rollback()
            continue
        except IntegrityError:
            service.db.rollback()
            continue
        except SQLAlchemyError:
            service.db.rollback()
            break

    # Fallback: reuse/create a deterministic guest account when random inserts fail.
    if user is None:
        fallback_email = os.getenv("GUEST_ACCOUNT_EMAIL", "guest@guest.local")
        fallback_password = os.getenv("GUEST_ACCOUNT_PASSWORD", "guest_access")
        try:
            user = service.get_user_by_email(fallback_email)
            if user is None:
                user = service.create_user(fallback_email, fallback_password)
        except SQLAlchemyError as e:
            service.db.rollback()
            logger.exception("Guest session creation failed", exc_info=e)
            # Log failed guest login
            audit_service.log_event(
                db=service.db,
                event_type="guest_login",
                status="failure",
                description="Could not create guest session",
                client_ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                request_path="/api/v1/auth/guest",
                request_method="POST",
                response_status=500,
                error_message="Guest session creation failed",
            )
            raise HTTPException(status_code=500, detail="Could not create guest session")

    issued = service.issue_session_tokens(
        user,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    # Log successful guest login
    audit_service.log_event(
        db=service.db,
        event_type="guest_login",
        status="success",
        user_id=user.id,
        description="Guest session created successfully",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path="/api/v1/auth/guest",
        request_method="POST",
        response_status=200,
    )
    return {
        "access_token": issued["access_token"],
        "refresh_token": issued["refresh_token"],
        "token_type": issued["token_type"],
    }

@app.post("/api/v1/auth/forgot-password", tags=["Auth"])
@limiter.limit("10/minute")
async def forgot_password(
    request: Request,
    req: ForgotPasswordRequest,
    service: UserService = Depends(get_user_service),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService())
):
    """Create a one-time reset token and dispatch via secure channel if account exists."""
    notification_service = NotificationService()
    user = service.get_user_by_email(req.email)
    response = {"message": "If this email exists, a reset link will be sent."}

    debug_expose_reset = os.getenv("AUTH_DEBUG_EXPOSE_RESET_TOKEN", "false").lower() == "true"
    reset_token = None
    if user:
        reset_token = service.create_password_reset_token(
            user,
            requested_ip=request.client.host if request.client else None,
        )

        # Integration point for email/SMS provider.
        logger.info(
            "Password reset token issued",
            extra={"user_id": user.id, "email_masked": _mask_email(req.email)}
        )
        notification_service.send_password_reset_email(user.email, reset_token)
        
        # Log forgot password request for existing user
        audit_service.log_event(
            db=service.db,
            event_type="forgot_password",
            status="success",
            user_id=user.id,
            description="Password reset token issued",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/forgot-password",
            request_method="POST",
            response_status=200,
        )
    else:
        # Log forgot password request for non-existent email (but don't expose that it doesn't exist)
        audit_service.log_event(
            db=service.db,
            event_type="forgot_password",
            status="success",  # Return success to avoid enumeration
            description="Password reset requested (account not found)",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/forgot-password",
            request_method="POST",
            response_status=200,
            metadata={"email_found": False}
        )

    if debug_expose_reset and reset_token:
        response["debug_reset_token"] = reset_token

    # Always return success to avoid email enumeration
    logger.info(
        "Password reset requested",
        extra={"email_masked": _mask_email(req.email), "exists": user is not None},
    )
    return response


@app.post("/api/v1/auth/reset-password", tags=["Auth"])
@limiter.limit("10/minute")
async def reset_password(
    request: Request,
    req: ResetPasswordRequest,
    service: UserService = Depends(get_user_service),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService())
):
    # Validate password strength
    try:
        validate_password_strength(req.new_password)
    except ValueError as e:
        # Log failed password reset attempt - weak password
        audit_service.log_event(
            db=service.db,
            event_type="password_reset",
            status="failure",
            description="Password reset failed - weak password",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/reset-password",
            request_method="POST",
            response_status=400,
            error_message=str(e),
            metadata={"reason": "weak_password"}
        )
        raise HTTPException(status_code=400, detail=str(e))
    
    ok = service.consume_password_reset_token(req.token, req.new_password)
    if not ok:
        # Log failed password reset attempt
        audit_service.log_event(
            db=service.db,
            event_type="password_reset",
            status="failure",
            description="Invalid or expired reset token",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/reset-password",
            request_method="POST",
            response_status=400,
            error_message="Invalid or expired reset token",
        )
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Log successful password reset (but note: we don't have user_id here since token was already consumed)
    audit_service.log_event(
        db=service.db,
        event_type="password_reset",
        status="success",
        description="Password reset successful",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path="/api/v1/auth/reset-password",
        request_method="POST",
        response_status=200,
    )
    return {"message": "Password reset successful"}


@app.post("/api/v1/auth/refresh", response_model=Token, tags=["Auth"])
@limiter.limit("30/minute")
async def refresh_token(
    request: Request,
    req: Optional[RefreshTokenRequest] = None,
    service: UserService = Depends(get_user_service),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService())
):
    raw_refresh_token = None
    if req and req.refresh_token:
        raw_refresh_token = req.refresh_token
    if not raw_refresh_token:
        raw_refresh_token = HttpOnlyCookieManager.get_refresh_token_from_cookie(request)

    if not raw_refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    issued = service.rotate_refresh_token(
        raw_refresh_token,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    if not issued:
        # Log failed token refresh attempt
        audit_service.log_event(
            db=service.db,
            event_type="token_refresh",
            status="failure",
            description="Invalid refresh token",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/refresh",
            request_method="POST",
            response_status=401,
            error_message="Invalid refresh token",
        )
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Log successful token refresh - extract user_id from issued tokens if possible
    user_id = issued.get('user_id') if isinstance(issued, dict) else None
    audit_service.log_event(
        db=service.db,
        event_type="token_refresh",
        status="success",
        user_id=user_id,
        description="Refresh token rotated successfully",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path="/api/v1/auth/refresh",
        request_method="POST",
        response_status=200,
    )
    response = JSONResponse(
        {
            "access_token": issued["access_token"],
            "refresh_token": issued["refresh_token"],
            "token_type": issued["token_type"],
        }
    )
    refresh_expires_at = issued.get("refresh_expires_at")
    if not refresh_expires_at:
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    HttpOnlyCookieManager.set_refresh_token_cookie(
        response=response,
        token=issued["refresh_token"],
        expires_at=refresh_expires_at,
        secure=os.getenv("PHIVERSITY_ENV") in {"prod", "production", "staging"},
    )
    csrf_token = generate_csrf_token()
    HttpOnlyCookieManager.set_csrf_token_cookie(
        response=response,
        token=csrf_token,
        secure=os.getenv("PHIVERSITY_ENV") in {"prod", "production", "staging"},
    )
    response.headers["X-CSRF-Token"] = csrf_token
    return response


@app.post("/api/v1/auth/logout", tags=["Auth"])
@limiter.limit("30/minute")
async def logout(
    request: Request,
    req: Optional[LogoutRequest] = None,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService())
):
    refresh_token_value = None
    if req and req.refresh_token:
        refresh_token_value = req.refresh_token
    if not refresh_token_value:
        refresh_token_value = HttpOnlyCookieManager.get_refresh_token_from_cookie(request)
    if refresh_token_value:
        service.revoke_refresh_token(refresh_token_value, reason="user_logout")

    payload = parse_access_token(token)
    jti = payload.get("jti")
    exp = payload.get("exp")
    if jti and exp:
        service.revoke_access_jti(
            jti=jti,
            user_id=current_user.id,
            expires_at=datetime.fromtimestamp(exp, tz=timezone.utc),
            reason="user_logout",
        )
    
    # Log successful logout
    audit_service.log_event(
        db=service.db,
        event_type="logout",
        status="success",
        user_id=current_user.id,
        description="User logged out successfully",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path="/api/v1/auth/logout",
        request_method="POST",
        response_status=200,
    )
    response = JSONResponse({"message": "Logged out"})
    HttpOnlyCookieManager.clear_refresh_token_cookie(response)
    HttpOnlyCookieManager.clear_csrf_token_cookie(response)
    return response


@app.post("/api/v1/auth/passwordless/request", tags=["Auth"])
@limiter.limit("10/minute")
async def request_passwordless_login(
    request: Request,
    req: PasswordlessRequest,
    service: UserService = Depends(get_user_service),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService()),
):
    """Issue one-time passwordless token (magic-link style)."""
    user = service.get_user_by_email(req.email)
    debug_token = None
    if user:
        token_service = PasswordlessService(service.db)
        raw_token = token_service.create_token(
            user=user,
            ttl_minutes=int(os.getenv("PASSWORDLESS_TOKEN_TTL_MINUTES", "15")),
            requested_ip=request.client.host if request.client else None,
        )
        if os.getenv("AUTH_DEBUG_EXPOSE_PASSWORDLESS_TOKEN", "false").lower() == "true":
            debug_token = raw_token
        audit_service.log_event(
            db=service.db,
            event_type="passwordless_requested",
            status="success",
            user_id=user.id,
            description="Passwordless token issued",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/passwordless/request",
            request_method="POST",
            response_status=200,
        )
    else:
        audit_service.log_event(
            db=service.db,
            event_type="passwordless_requested",
            status="success",
            description="Passwordless requested for unknown email",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/passwordless/request",
            request_method="POST",
            response_status=200,
        )

    return {
        "message": "If this email exists, a passwordless sign-in link has been sent",
        "debug_token": debug_token,
    }


@app.post("/api/v1/auth/passwordless/verify", response_model=Token, tags=["Auth"])
@limiter.limit("20/minute")
async def verify_passwordless_login(
    request: Request,
    req: PasswordlessVerifyRequest,
    service: UserService = Depends(get_user_service),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService()),
):
    """Consume one-time passwordless token and issue auth session tokens."""
    token_service = PasswordlessService(service.db)
    user = token_service.consume_token(req.token)
    if not user:
        audit_service.log_event(
            db=service.db,
            event_type="passwordless_verify",
            status="failure",
            description="Invalid or expired passwordless token",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/passwordless/verify",
            request_method="POST",
            response_status=400,
            error_message="Invalid or expired token",
        )
        raise HTTPException(status_code=400, detail="Invalid or expired passwordless token")

    issued = service.issue_session_tokens(
        user,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    audit_service.log_event(
        db=service.db,
        event_type="passwordless_verify",
        status="success",
        user_id=user.id,
        description="Passwordless login successful",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path="/api/v1/auth/passwordless/verify",
        request_method="POST",
        response_status=200,
    )

    response = JSONResponse(
        {
            "access_token": issued["access_token"],
            "refresh_token": issued["refresh_token"],
            "token_type": issued["token_type"],
        }
    )
    refresh_expires_at = issued.get("refresh_expires_at")
    if not refresh_expires_at:
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    secure_cookies = os.getenv("PHIVERSITY_ENV") in {"prod", "production", "staging"}
    HttpOnlyCookieManager.set_refresh_token_cookie(
        response=response,
        token=issued["refresh_token"],
        expires_at=refresh_expires_at,
        secure=secure_cookies,
    )
    csrf_token = generate_csrf_token()
    HttpOnlyCookieManager.set_csrf_token_cookie(
        response=response,
        token=csrf_token,
        secure=secure_cookies,
    )
    response.headers["X-CSRF-Token"] = csrf_token
    return response


@app.post("/api/v1/auth/email/verify-send", tags=["Auth"])
@limiter.limit("5/minute")
async def send_verification_email(
    request: Request,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService())
):
    """Send email verification link to current user's email."""
    email_service = EmailVerificationService(service.db)
    notification_service = NotificationService()

    # Check if already verified
    if current_user.email_verified:
        return {
            "message": "Email already verified",
            "email_verified": True,
        }

    # Create verification token
    raw_token = email_service.create_verification_token(
        current_user,
        requested_ip=request.client.host if request.client else None,
    )

    # Log event
    audit_service.log_event(
        db=service.db,
        event_type="email_verification_requested",
        status="success",
        user_id=current_user.id,
        description="Email verification token generated",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path="/api/v1/auth/email/verify-send",
        request_method="POST",
        response_status=200,
    )

    notification_service.send_verification_email(current_user.email, raw_token)

    return {
        "message": "Verification email sent",
        "email": current_user.email,
        "debug_token": raw_token if os.getenv("AUTH_DEBUG_EXPOSE_RESET_TOKEN") == "true" else None,
    }


@app.post("/api/v1/auth/email/verify", tags=["Auth"])
@limiter.limit("10/minute")
async def verify_email(
    request: Request,
    req: dict,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService())
):
    """Verify email with token from email link."""
    token = req.get("token", "")
    if not token:
        raise HTTPException(status_code=400, detail="Verification token required")

    email_service = EmailVerificationService(service.db)

    # Verify token
    ok = email_service.verify_email_token(current_user.id, token)
    if not ok:
        # Log failed verification attempt
        audit_service.log_event(
            db=service.db,
            event_type="email_verification",
            status="failure",
            user_id=current_user.id,
            description="Invalid or expired verification token",
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_path="/api/v1/auth/email/verify",
            request_method="POST",
            response_status=400,
            error_message="Invalid or expired token",
        )
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    # Log successful verification
    audit_service.log_event(
        db=service.db,
        event_type="email_verification",
        status="success",
        user_id=current_user.id,
        description="Email verified successfully",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path="/api/v1/auth/email/verify",
        request_method="POST",
        response_status=200,
    )

    return {
        "message": "Email verified successfully",
        "email": current_user.email,
        "email_verified": True,
    }


@app.get("/api/v1/auth/email/status", tags=["Auth"])
@limiter.limit("30/minute")
async def check_email_verification_status(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Check if current user's email is verified."""
    email_service = EmailVerificationService(service.db)
    pending_token = email_service.get_pending_verification_token(current_user.id)

    return {
        "email": current_user.email,
        "email_verified": current_user.email_verified,
        "email_verified_at": current_user.email_verified_at.isoformat() if current_user.email_verified_at else None,
        "pending_verification": pending_token is not None,
        "pending_expires_at": pending_token.expires_at.isoformat() if pending_token else None,
    }


@app.post("/api/v1/auth/email/resend", tags=["Auth"])
@limiter.limit("3/minute")
async def resend_verification_email(
    request: Request,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService())
):
    """Resend email verification link (rate limited)."""
    email_service = EmailVerificationService(service.db)
    notification_service = NotificationService()

    if current_user.email_verified:
        return {"message": "Email already verified", "email_verified": True}

    # Create new verification token (invalidates old ones)
    raw_token = email_service.resend_verification_token(
        current_user,
        requested_ip=request.client.host if request.client else None,
    )
    notification_service.send_verification_email(current_user.email, raw_token)

    # Log event
    audit_service.log_event(
        db=service.db,
        event_type="email_verification_resent",
        status="success",
        user_id=current_user.id,
        description="Email verification token regenerated",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path="/api/v1/auth/email/resend",
        request_method="POST",
        response_status=200,
    )

    return {
        "message": "Verification email resent",
        "email": current_user.email,
        "debug_token": raw_token if os.getenv("AUTH_DEBUG_EXPOSE_RESET_TOKEN") == "true" else None,
    }



@app.get("/api/v1/auth/sessions", tags=["Auth"])
@limiter.limit("30/minute")
async def list_user_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """List active refresh-token-backed sessions for the current user."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    sessions = (
        service.db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > now,
        )
        .order_by(RefreshToken.created_at.desc())
        .all()
    )
    return {
        "sessions": [
            {
                "id": s.id,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "expires_at": s.expires_at.isoformat() if s.expires_at else None,
                "created_ip": s.created_ip,
                "created_user_agent": s.created_user_agent,
                "family_id": s.family_id,
            }
            for s in sessions
        ],
        "count": len(sessions),
    }


@app.delete("/api/v1/auth/sessions/{session_id}", tags=["Auth"])
@limiter.limit("20/minute")
async def revoke_user_session(
    request: Request,
    session_id: int,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService()),
):
    """Revoke a specific refresh-token session belonging to current user."""
    session = (
        service.db.query(RefreshToken)
        .filter(RefreshToken.id == session_id, RefreshToken.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)
        session.revoked_reason = "session_revoked_by_user"
        service.db.commit()

    audit_service.log_event(
        db=service.db,
        event_type="session_revoke",
        status="success",
        user_id=current_user.id,
        description=f"Session {session_id} revoked",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path=f"/api/v1/auth/sessions/{session_id}",
        request_method="DELETE",
        response_status=200,
    )

    return {"message": "Session revoked", "session_id": session_id}


@app.delete("/api/v1/auth/sessions", tags=["Auth"])
@limiter.limit("10/minute")
async def revoke_all_user_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService()),
):
    """Revoke all active refresh-token sessions for current user."""
    count = service.revoke_all_user_refresh_tokens(current_user.id, reason="all_sessions_revoked_by_user")

    audit_service.log_event(
        db=service.db,
        event_type="session_revoke_all",
        status="success",
        user_id=current_user.id,
        description=f"Revoked {count} session(s)",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path="/api/v1/auth/sessions",
        request_method="DELETE",
        response_status=200,
        metadata={"revoked_count": count},
    )

    response = JSONResponse({"message": "All sessions revoked", "revoked_count": count})
    HttpOnlyCookieManager.clear_refresh_token_cookie(response)
    HttpOnlyCookieManager.clear_csrf_token_cookie(response)
    return response


@app.post("/api/v1/auth/mfa/setup", tags=["Auth"])
@limiter.limit("10/minute")
async def setup_mfa(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Generate a new TOTP secret and backup codes for the current user."""
    mfa_service = MFAService()
    secret = mfa_service.generate_secret()
    backup_codes = mfa_service.generate_backup_codes()
    backup_hashes = [mfa_service.hash_backup_code(code) for code in backup_codes]

    current_user.mfa_secret_encrypted = mfa_service.encrypt_secret(secret)
    current_user.mfa_backup_codes_encrypted = mfa_service.encode_backup_hashes(backup_hashes)
    current_user.mfa_enabled = False
    service.db.commit()

    return {
        "secret": secret,
        "otpauth_uri": mfa_service.provisioning_uri(secret, current_user.email),
        "backup_codes": backup_codes,
        "message": "Verify with /api/v1/auth/mfa/enable to activate MFA",
    }


@app.post("/api/v1/auth/mfa/enable", tags=["Auth"])
@limiter.limit("20/minute")
async def enable_mfa(
    request: Request,
    req: MFAConfirmRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService()),
):
    """Enable MFA after proving ownership of the generated TOTP secret."""
    if not current_user.mfa_secret_encrypted:
        raise HTTPException(status_code=400, detail="MFA setup required first")

    mfa_service = MFAService()
    secret = mfa_service.decrypt_secret(current_user.mfa_secret_encrypted)
    if not mfa_service.verify_totp(secret, req.code):
        raise HTTPException(status_code=400, detail="Invalid MFA code")

    current_user.mfa_enabled = True
    service.db.commit()

    audit_service.log_event(
        db=service.db,
        event_type="mfa_enabled",
        status="success",
        user_id=current_user.id,
        description="User enabled TOTP MFA",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path="/api/v1/auth/mfa/enable",
        request_method="POST",
        response_status=200,
    )

    return {"message": "MFA enabled"}


@app.post("/api/v1/auth/mfa/disable", tags=["Auth"])
@limiter.limit("20/minute")
async def disable_mfa(
    request: Request,
    req: MFAConfirmRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Disable MFA using a current TOTP code."""
    if not current_user.mfa_enabled or not current_user.mfa_secret_encrypted:
        raise HTTPException(status_code=400, detail="MFA is not enabled")

    mfa_service = MFAService()
    secret = mfa_service.decrypt_secret(current_user.mfa_secret_encrypted)
    if not mfa_service.verify_totp(secret, req.code):
        raise HTTPException(status_code=400, detail="Invalid MFA code")

    current_user.mfa_enabled = False
    current_user.mfa_secret_encrypted = None
    current_user.mfa_backup_codes_encrypted = None
    service.db.commit()
    return {"message": "MFA disabled"}


@app.post("/api/v1/auth/mfa/recover", tags=["Auth"])
@limiter.limit("20/minute")
async def recover_with_backup_code(
    request: Request,
    req: MFABackupRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Consume a backup code during account recovery."""
    if not current_user.mfa_backup_codes_encrypted:
        raise HTTPException(status_code=400, detail="No backup codes configured")

    mfa_service = MFAService()
    hashes = mfa_service.decode_backup_hashes(current_user.mfa_backup_codes_encrypted)
    backup_hash = mfa_service.hash_backup_code(req.backup_code.upper())
    if backup_hash not in hashes:
        raise HTTPException(status_code=400, detail="Invalid backup code")

    hashes.remove(backup_hash)
    current_user.mfa_backup_codes_encrypted = mfa_service.encode_backup_hashes(hashes)
    service.db.commit()
    return {"message": "Backup code accepted", "remaining_backup_codes": len(hashes)}


@app.post("/api/v1/auth/api-keys", tags=["Auth"])
@limiter.limit("10/minute")
async def create_api_key(
    request: Request,
    req: APIKeyCreateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Create an API key for service-to-service auth."""
    api_key_service = APIKeyService(service.db)
    expires_at = None
    if req.expires_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=req.expires_days)
    raw_key, row = api_key_service.create_key(
        user_id=current_user.id,
        name=req.name,
        scopes=req.scopes,
        expires_at=expires_at,
    )
    return {
        "key_id": row.id,
        "name": row.name,
        "api_key": raw_key,
        "key_prefix": row.key_prefix,
        "scopes": req.scopes,
        "expires_at": row.expires_at.isoformat() if row.expires_at else None,
        "message": "Store this key securely; it cannot be retrieved again",
    }


@app.get("/api/v1/auth/api-keys", tags=["Auth"])
@limiter.limit("30/minute")
async def list_api_keys(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """List API keys for current user without exposing secret material."""
    api_key_service = APIKeyService(service.db)
    rows = api_key_service.list_keys(current_user.id)
    return {
        "api_keys": [
            {
                "id": row.id,
                "name": row.name,
                "key_prefix": row.key_prefix,
                "is_active": row.is_active,
                "scopes": json.loads(row.scopes or "[]"),
                "expires_at": row.expires_at.isoformat() if row.expires_at else None,
                "last_used_at": row.last_used_at.isoformat() if row.last_used_at else None,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ],
        "count": len(rows),
    }


@app.delete("/api/v1/auth/api-keys", tags=["Auth"])
@limiter.limit("20/minute")
async def revoke_api_key(
    request: Request,
    req: APIKeyRevokeRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Revoke one API key by ID."""
    api_key_service = APIKeyService(service.db)
    ok = api_key_service.revoke_key(current_user.id, req.key_id)
    if not ok:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"message": "API key revoked", "key_id": req.key_id}


@app.post("/api/v1/auth/api-keys/verify", tags=["Auth"])
@limiter.limit("30/minute")
async def verify_api_key(
    request: Request,
    req: APIKeyVerifyRequest,
    service: UserService = Depends(get_user_service),
):
    """Validate API key and return metadata for debugging/integration tests."""
    api_key_service = APIKeyService(service.db)
    row = api_key_service.verify_key(req.api_key)
    if not row:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {
        "valid": True,
        "key_id": row.id,
        "user_id": row.user_id,
        "scopes": json.loads(row.scopes or "[]"),
    }


@app.get("/api/v1/oauth/.well-known/openid-configuration", tags=["OAuth2"])
async def oauth_openid_configuration(request: Request):
    """OpenID discovery scaffold for local OAuth2 integration testing."""
    issuer = os.getenv("OAUTH_ISSUER", str(request.base_url).rstrip("/"))
    return {
        "issuer": issuer,
        "authorization_endpoint": f"{issuer}/api/v1/oauth/authorize",
        "token_endpoint": f"{issuer}/api/v1/oauth/token",
        "jwks_uri": f"{issuer}/api/v1/oauth/jwks",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "client_credentials"],
        "token_endpoint_auth_methods_supported": ["client_secret_post"],
        "scopes_supported": ["read_jobs", "create_jobs", "update_jobs", "user:read", "admin"],
        "code_challenge_methods_supported": ["S256", "plain"],
    }


@app.get("/api/v1/oauth/jwks", tags=["OAuth2"])
async def oauth_jwks():
    """JWKS scaffold. HS256 key material is intentionally not exposed."""
    keyring = JWTKeyRing()
    return {
        "keys": [
            {
                "kty": "oct",
                "alg": "HS256",
                "use": "sig",
                "kid": keyring.get_current_key_id() or "legacy-hs256",
            }
        ]
    }


@app.post("/api/v1/admin/oauth/clients", tags=["OAuth2", "Admin"])
@limiter.limit("20/minute")
async def create_oauth_client(
    request: Request,
    req: OAuthClientCreateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService()),
):
    """Register OAuth2 client credentials for provider scaffolding."""
    _require_admin(current_user)
    oauth_service = OAuthScaffoldService(service.db)
    row, raw_secret = oauth_service.create_client(
        name=req.name,
        redirect_uris=req.redirect_uris,
        scopes=req.scopes,
        grants=req.grants,
    )

    audit_service.log_event(
        db=service.db,
        event_type="oauth_client_created",
        status="success",
        user_id=current_user.id,
        description=f"OAuth client created: {row.client_id}",
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path="/api/v1/admin/oauth/clients",
        request_method="POST",
        response_status=200,
    )

    return {
        "client_id": row.client_id,
        "client_secret": raw_secret,
        "name": row.name,
        "redirect_uris": _json_text_to_list(row.redirect_uris),
        "scopes": _json_text_to_list(row.scopes),
        "grants": _json_text_to_list(row.grants),
        "message": "Client secret is shown once; store it securely",
    }


@app.get("/api/v1/admin/oauth/clients", tags=["OAuth2", "Admin"])
async def list_oauth_clients(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    _require_admin(current_user)
    rows = service.db.query(OAuthClient).order_by(OAuthClient.created_at.desc()).all()
    return {
        "clients": [
            {
                "id": row.id,
                "client_id": row.client_id,
                "name": row.name,
                "redirect_uris": _json_text_to_list(row.redirect_uris),
                "scopes": _json_text_to_list(row.scopes),
                "grants": _json_text_to_list(row.grants),
                "is_active": row.is_active,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ],
        "count": len(rows),
    }


@app.get("/api/v1/oauth/authorize", tags=["OAuth2"])
@limiter.limit("60/minute")
async def oauth_authorize(
    request: Request,
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: str = "",
    state: Optional[str] = None,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Authorization endpoint scaffold that returns a redirect URL with auth code."""
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Only response_type=code is supported")

    client = (
        service.db.query(OAuthClient)
        .filter(OAuthClient.client_id == client_id, OAuthClient.is_active == True)
        .first()
    )
    if not client:
        raise HTTPException(status_code=400, detail="Unknown OAuth client")

    allowed_redirect_uris = _json_text_to_list(client.redirect_uris)
    if redirect_uri not in allowed_redirect_uris:
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")

    if code_challenge_method and code_challenge_method not in {"S256", "plain"}:
        raise HTTPException(status_code=400, detail="Unsupported code_challenge_method")

    oauth_service = OAuthScaffoldService(service.db)
    raw_code = oauth_service.create_authorization_code(
        client_id=client_id,
        user_id=current_user.id,
        redirect_uri=redirect_uri,
        scope=scope,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )

    query = {"code": raw_code}
    if state is not None:
        query["state"] = state

    return {
        "redirect_to": f"{redirect_uri}?{urlencode(query)}",
        "code": raw_code,
        "state": state,
        "note": "Scaffold endpoint: production integrations should perform actual HTTP redirect",
    }


@app.post("/api/v1/oauth/token", tags=["OAuth2"])
@limiter.limit("120/minute")
async def oauth_token(request: Request, service: UserService = Depends(get_user_service)):
    """OAuth2 token endpoint scaffold supporting authorization_code and client_credentials grants."""
    form = await request.form()
    grant_type = str(form.get("grant_type", "")).strip()
    client_id = str(form.get("client_id", "")).strip()
    client_secret = str(form.get("client_secret", "")).strip()

    oauth_service = OAuthScaffoldService(service.db)

    if grant_type == "authorization_code":
        code = str(form.get("code", "")).strip()
        redirect_uri = str(form.get("redirect_uri", "")).strip()
        code_verifier = str(form.get("code_verifier", "")).strip()

        client = oauth_service.verify_client(client_id, client_secret)
        if not client:
            raise HTTPException(status_code=401, detail="Invalid client credentials")

        code_row = oauth_service.consume_authorization_code(
            raw_code=code,
            client_id=client_id,
            redirect_uri=redirect_uri,
        )
        if not code_row:
            raise HTTPException(status_code=400, detail="Invalid authorization code")

        if code_row.code_challenge:
            if not code_verifier:
                raise HTTPException(status_code=400, detail="code_verifier required")
            method = code_row.code_challenge_method or "plain"
            calculated = _pkce_s256_challenge(code_verifier) if method == "S256" else code_verifier
            if calculated != code_row.code_challenge:
                raise HTTPException(status_code=400, detail="PKCE verification failed")

        user = service.db.query(User).filter(User.id == code_row.user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="Authorization code user not found")

        scopes = [s for s in (code_row.scope or "").split(" ") if s]
        access_token = create_access_token(
            data={"sub": user.email, "aud": client_id},
            scopes=scopes or _json_text_to_list(client.scopes),
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1800,
            "scope": " ".join(scopes),
        }

    if grant_type == "client_credentials":
        client = oauth_service.verify_client(client_id, client_secret)
        if not client:
            raise HTTPException(status_code=401, detail="Invalid client credentials")

        requested_scope = str(form.get("scope", "")).strip()
        allowed_scopes = set(_json_text_to_list(client.scopes))
        wanted_scopes = [s for s in requested_scope.split(" ") if s] if requested_scope else []
        granted_scopes = [s for s in wanted_scopes if s in allowed_scopes] if wanted_scopes else list(allowed_scopes)

        access_token = create_access_token(
            data={"sub": f"client:{client_id}", "aud": client_id},
            scopes=granted_scopes,
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1800,
            "scope": " ".join(granted_scopes),
        }

    raise HTTPException(status_code=400, detail="Unsupported grant_type")

@app.post("/api/v1/auth/webauthn/register/options", tags=["WebAuthn", "Auth"])
@limiter.limit("20/minute")
async def webauthn_register_options(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Return WebAuthn registration options scaffold for frontend integration."""
    _prune_webauthn_challenges()
    challenge = secrets.token_urlsafe(32)
    _WEBAUTHN_CHALLENGES[f"register:{current_user.id}:{challenge}"] = (
        datetime.now(timezone.utc) + timedelta(seconds=_WEBAUTHN_CHALLENGE_TTL_SECONDS)
    )
    return {
        "challenge": challenge,
        "rp": {
            "id": os.getenv("WEBAUTHN_RP_ID", "localhost"),
            "name": os.getenv("WEBAUTHN_RP_NAME", "Phiversity"),
        },
        "user": {
            "id": str(current_user.id),
            "name": current_user.email,
            "displayName": current_user.email,
        },
        "note": "Scaffold response: perform full WebAuthn ceremony on frontend",
    }


@app.post("/api/v1/auth/webauthn/register/verify", tags=["WebAuthn", "Auth"])
@limiter.limit("20/minute")
async def webauthn_register_verify(
    request: Request,
    req: WebAuthnRegisterVerifyRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Persist WebAuthn credential scaffold after frontend ceremony completion."""
    challenge_key = f"register:{current_user.id}:{req.challenge}"
    expires_at = _WEBAUTHN_CHALLENGES.get(challenge_key)
    if not expires_at or expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired registration challenge")

    existing = (
        service.db.query(WebAuthnCredential)
        .filter(WebAuthnCredential.credential_id == req.credential_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Credential already registered")

    row = WebAuthnCredential(
        user_id=current_user.id,
        credential_id=req.credential_id,
        public_key=req.public_key,
        sign_count=req.sign_count,
        aaguid=req.aaguid,
        transports=json.dumps(req.transports),
    )
    service.db.add(row)
    service.db.commit()
    _WEBAUTHN_CHALLENGES.pop(challenge_key, None)

    return {
        "message": "WebAuthn credential registered",
        "credential_id": row.credential_id,
    }


@app.post("/api/v1/auth/webauthn/authenticate/options", tags=["WebAuthn", "Auth"])
@limiter.limit("30/minute")
async def webauthn_authenticate_options(
    request: Request,
    req: PasswordlessRequest,
    service: UserService = Depends(get_user_service),
):
    """Return authentication challenge for registered WebAuthn credentials."""
    _prune_webauthn_challenges()
    user = service.get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    creds = (
        service.db.query(WebAuthnCredential)
        .filter(WebAuthnCredential.user_id == user.id)
        .all()
    )
    if not creds:
        raise HTTPException(status_code=404, detail="No WebAuthn credentials registered")

    challenge = secrets.token_urlsafe(32)
    _WEBAUTHN_CHALLENGES[f"auth:{user.id}:{challenge}"] = (
        datetime.now(timezone.utc) + timedelta(seconds=_WEBAUTHN_CHALLENGE_TTL_SECONDS)
    )
    return {
        "challenge": challenge,
        "rp_id": os.getenv("WEBAUTHN_RP_ID", "localhost"),
        "allow_credentials": [{"id": c.credential_id, "type": "public-key"} for c in creds],
        "note": "Scaffold response: cryptographic assertion verification should be implemented next",
    }


@app.post("/api/v1/auth/webauthn/authenticate/verify", response_model=Token, tags=["WebAuthn", "Auth"])
@limiter.limit("30/minute")
async def webauthn_authenticate_verify(
    request: Request,
    req: WebAuthnAuthenticateRequest,
    service: UserService = Depends(get_user_service),
):
    """Verify WebAuthn authentication scaffold and issue tokens."""
    user = service.get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid authentication request")

    challenge_key = f"auth:{user.id}:{req.challenge}"
    expires_at = _WEBAUTHN_CHALLENGES.get(challenge_key)
    if not expires_at or expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired authentication challenge")

    credential = (
        service.db.query(WebAuthnCredential)
        .filter(WebAuthnCredential.user_id == user.id, WebAuthnCredential.credential_id == req.credential_id)
        .first()
    )
    if not credential:
        raise HTTPException(status_code=400, detail="Unknown WebAuthn credential")

    _WEBAUTHN_CHALLENGES.pop(challenge_key, None)
    credential.sign_count = int(credential.sign_count or 0) + 1
    credential.last_used_at = datetime.now(timezone.utc)
    service.db.commit()

    issued = service.issue_session_tokens(
        user,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    response = JSONResponse(
        {
            "access_token": issued["access_token"],
            "refresh_token": issued["refresh_token"],
            "token_type": issued["token_type"],
        }
    )
    refresh_expires_at = issued.get("refresh_expires_at")
    if not refresh_expires_at:
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    secure_cookies = os.getenv("PHIVERSITY_ENV") in {"prod", "production", "staging"}
    HttpOnlyCookieManager.set_refresh_token_cookie(
        response=response,
        token=issued["refresh_token"],
        expires_at=refresh_expires_at,
        secure=secure_cookies,
    )
    csrf_token = generate_csrf_token()
    HttpOnlyCookieManager.set_csrf_token_cookie(
        response=response,
        token=csrf_token,
        secure=secure_cookies,
    )
    response.headers["X-CSRF-Token"] = csrf_token
    return response


@app.post("/api/v1/admin/saml/providers", tags=["SAML", "Admin"])
@limiter.limit("20/minute")
async def create_saml_provider(
    request: Request,
    req: SAMLProviderCreateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Create SAML IdP configuration scaffold."""
    _require_admin(current_user)
    row = SAMLIdentityProvider(
        name=req.name,
        entity_id=req.entity_id,
        sso_url=req.sso_url,
        x509_cert=req.x509_cert,
        acs_url=req.acs_url,
        is_active=True,
    )
    service.db.add(row)
    service.db.commit()
    service.db.refresh(row)
    return {
        "provider_id": row.id,
        "name": row.name,
        "entity_id": row.entity_id,
        "sso_url": row.sso_url,
        "acs_url": row.acs_url,
        "is_active": row.is_active,
    }


@app.get("/api/v1/auth/saml/metadata", tags=["SAML", "Auth"])
async def saml_metadata(request: Request):
    """Expose SAML metadata scaffold for IdP setup."""
    entity_id = os.getenv("SAML_SP_ENTITY_ID", str(request.base_url).rstrip("/"))
    acs_url = os.getenv("SAML_SP_ACS_URL", f"{str(request.base_url).rstrip('/')}/api/v1/auth/saml/acs")
    metadata = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        f"<EntityDescriptor entityID=\"{entity_id}\" xmlns=\"urn:oasis:names:tc:SAML:2.0:metadata\">"
        "<SPSSODescriptor protocolSupportEnumeration=\"urn:oasis:names:tc:SAML:2.0:protocol\">"
        f"<AssertionConsumerService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST\" Location=\"{acs_url}\" index=\"0\"/>"
        "</SPSSODescriptor>"
        "</EntityDescriptor>"
    )
    return FastAPIResponse(content=metadata, media_type="application/samlmetadata+xml")


@app.get("/api/v1/auth/saml/login", tags=["SAML", "Auth"])
@limiter.limit("30/minute")
async def saml_login_redirect(
    request: Request,
    provider_id: int,
    relay_state: Optional[str] = None,
    service: UserService = Depends(get_user_service),
):
    """Return IdP redirect URL scaffold for SAML sign-in initiation."""
    provider = (
        service.db.query(SAMLIdentityProvider)
        .filter(SAMLIdentityProvider.id == provider_id, SAMLIdentityProvider.is_active == True)
        .first()
    )
    if not provider:
        raise HTTPException(status_code=404, detail="SAML provider not found")

    query = {
        "SAMLRequest": "PHIVERSITY_SCAFFOLD_REQUEST",
    }
    if relay_state:
        query["RelayState"] = relay_state

    return {
        "redirect_to": f"{provider.sso_url}?{urlencode(query)}",
        "provider_id": provider.id,
        "note": "Scaffold response: production should build signed AuthnRequest",
    }


@app.post("/api/v1/auth/saml/acs", tags=["SAML", "Auth"])
@limiter.limit("30/minute")
async def saml_acs(
    request: Request,
    req: SAMLACSRequest,
    service: UserService = Depends(get_user_service),
):
    """SAML ACS scaffold. Optionally accepts email_hint in development mode."""
    allow_dev_hint = os.getenv("SAML_SCAFFOLD_ACCEPT_EMAIL_HINT", "false").lower() in {"1", "true", "yes"}
    if not allow_dev_hint or not req.email_hint:
        raise HTTPException(
            status_code=501,
            detail="SAML ACS scaffold only. Enable SAML_SCAFFOLD_ACCEPT_EMAIL_HINT for dev smoke testing.",
        )

    user = service.get_user_by_email(req.email_hint)
    if not user:
        raise HTTPException(status_code=400, detail="No local user for provided email_hint")

    issued = service.issue_session_tokens(
        user,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    response = JSONResponse(
        {
            "access_token": issued["access_token"],
            "refresh_token": issued["refresh_token"],
            "token_type": issued["token_type"],
            "relay_state": req.relay_state,
        }
    )
    refresh_expires_at = issued.get("refresh_expires_at")
    if not refresh_expires_at:
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    secure_cookies = os.getenv("PHIVERSITY_ENV") in {"prod", "production", "staging"}
    HttpOnlyCookieManager.set_refresh_token_cookie(
        response=response,
        token=issued["refresh_token"],
        expires_at=refresh_expires_at,
        secure=secure_cookies,
    )
    csrf_token = generate_csrf_token()
    HttpOnlyCookieManager.set_csrf_token_cookie(
        response=response,
        token=csrf_token,
        secure=secure_cookies,
    )
    response.headers["X-CSRF-Token"] = csrf_token
    return response


@app.post("/api/v1/auth/password-strength", tags=["Auth"], include_in_schema=True)
@limiter.limit("30/minute")
async def check_password_strength(
    request: Request,
    req: dict = None,
):

    """
    Check password strength and return detailed feedback.
    Useful for real-time password validation on frontend.
    
    Request body: {"password": "user_password"}
    """
    if not req:
        raise HTTPException(status_code=400, detail="Request body required")
    
    password = req.get("password", "")
    feedback = get_password_strength_feedback(password)
    
    return {
        "password_strength": feedback["strength"],
        "score": feedback["score"],
        "issues": feedback["issues"],
        "suggestions": feedback["suggestions"],
    }


# --- Admin Audit & Security Dashboard ---

@app.get("/api/v1/admin/security-events", tags=["Admin"])
async def get_security_events(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    limit: int = 100,
    offset: int = 0,
    severity: Optional[str] = None,
):
    """List security events for SOC2/HIPAA operational visibility."""
    _require_admin(current_user)

    query = service.db.query(SecurityEvent)
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    rows = query.order_by(SecurityEvent.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "security_events": [
            {
                "id": row.id,
                "user_id": row.user_id,
                "event_type": row.event_type,
                "severity": row.severity,
                "source": row.source,
                "description": row.description,
                "client_ip": row.client_ip,
                "metadata": json.loads(row.event_metadata or "{}"),
                "notified_at": row.notified_at.isoformat() if row.notified_at else None,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ],
        "count": len(rows),
    }


@app.get("/api/v1/admin/compliance/audit-export", tags=["Admin"])
async def export_compliance_audit_logs(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    limit: int = 500,
    offset: int = 0,
):
    """Export audit and security event trail for compliance controls."""
    _require_admin(current_user)

    audit_service = AuditService()
    logs = audit_service.get_audit_logs(db=service.db, limit=limit, offset=offset)
    events = (
        service.db.query(SecurityEvent)
        .order_by(SecurityEvent.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "audit_logs": [
            {
                "id": log.id,
                "event_type": log.event_type,
                "status": log.status,
                "user_id": log.user_id,
                "client_ip": log.client_ip,
                "request_path": log.request_path,
                "request_method": log.request_method,
                "response_status": log.response_status,
                "metadata": log.audit_metadata,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "security_events": [
            {
                "id": row.id,
                "event_type": row.event_type,
                "severity": row.severity,
                "user_id": row.user_id,
                "source": row.source,
                "client_ip": row.client_ip,
                "metadata": row.event_metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in events
        ],
        "audit_count": len(logs),
        "security_event_count": len(events),
    }

@app.get("/api/v1/admin/audit-logs", tags=["Admin"])
async def get_audit_logs(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    limit: int = 100,
    offset: int = 0,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
):
    """View system audit logs (admin only)"""
    _require_admin(current_user)
    
    audit_service = AuditService()
    event_types = [event_type] if event_type else None
    
    logs = audit_service.get_audit_logs(
        db=service.db,
        limit=limit,
        offset=offset,
        event_types=event_types,
        status=status,
    )
    
    return {
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "event_type": log.event_type,
                "status": log.status,
                "description": log.description,
                "client_ip": log.client_ip,
                "request_path": log.request_path,
                "response_status": log.response_status,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "count": len(logs),
    }


@app.get("/api/v1/admin/user-audit-trail/{user_id}", tags=["Admin"])
async def get_user_audit_trail(
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    limit: int = 50,
    offset: int = 0,
):
    """View audit trail for a specific user (admin only)"""
    _require_admin(current_user)
    
    audit_service = AuditService()
    logs = audit_service.get_user_audit_trail(
        db=service.db,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    
    return {
        "user_id": user_id,
        "logs": [
            {
                "id": log.id,
                "event_type": log.event_type,
                "status": log.status,
                "description": log.description,
                "client_ip": log.client_ip,
                "response_status": log.response_status,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "count": len(logs),
    }


@app.get("/api/v1/admin/jwt-key-rotation/status", tags=["Admin"])
async def get_jwt_key_rotation_status(
    current_user: User = Depends(get_current_user),
):
    """Get JWT key rotation status (admin only)"""
    _require_admin(current_user)
    
    keyring = JWTKeyRing()
    schedule = keyring.get_key_rotation_schedule()
    
    return {
        "jwt_key_rotation": schedule,
    }


@app.post("/api/v1/admin/jwt-key-rotation/rotate", tags=["Admin"])
async def rotate_jwt_key(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    audit_service: AuditService = Depends(lambda db=Depends(get_db): AuditService())
):
    """Manually rotate JWT signing key (admin only)"""
    _require_admin(current_user)
    
    import secrets
    
    # Generate new signing key (in production, use proper key derivation)
    new_key = secrets.token_urlsafe(32)
    
    keyring = JWTKeyRing()
    kid = keyring.rotate_key(new_key)
    
    # Log key rotation
    audit_service.log_event(
        db=service.db,
        event_type="jwt_key_rotated",
        status="success",
        user_id=current_user.id,
        description=f"JWT signing key rotated (kid: {kid})",
        response_status=200,
    )
    
    return {
        "message": "JWT key rotated successfully",
        "kid": kid,
        "schedule": keyring.get_key_rotation_schedule(),
    }


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
    scoped_key = _scoped_idempotency_key(current_user.id, req.idempotency_key)
    if scoped_key:
        existing = service.db.query(JobModel).filter(
            JobModel.idempotency_key == scoped_key
        ).first()
        if existing:
            return {"job_id": existing.id, "status": existing.status}

    job = service.create_job()
    job.user_id = current_user.id
    if scoped_key:
        job.idempotency_key = scoped_key
    service.db.commit()
    service.start_background_job(job.id, req.model_dump())
    return {"job_id": job.id, "status": "queued"}

@app.get("/api/v1/jobs", response_model=List[JobResponse], tags=["Jobs"])
async def list_jobs(
    service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
    """List recent jobs for the current user"""
    jobs = service.db.query(JobModel).filter(JobModel.user_id == current_user.id).order_by(JobModel.created_at.desc()).limit(10).all()
    result = []
    for j in jobs:
        problem = ""
        if j.request_payload:
            try:
                payload = json.loads(j.request_payload)
                problem = payload.get("problem", "")
            except (json.JSONDecodeError, TypeError):
                pass
        result.append({"job_id": j.id, "status": j.status, "problem": problem})
    return result

@app.get("/api/v1/jobs/{job_id}", response_model=JobStatusResponse, tags=["Jobs"])
async def get_job_status(
    job_id: str,
    service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
    db_job = _get_owned_job_or_404(job_id, service, current_user)
        
    log_content = db_job.log or ""
    if len(log_content) > 10000:
        log_content = "...[truncated]...\n" + log_content[-10000:]
        
    artifact_urls = _job_artifact_urls(db_job)
    summary = service.extract_job_summary(db_job)

    response_data = {
        "status": db_job.status,
        "log": log_content,
        "progress": db_job.progress,
        "video_url": artifact_urls["video_url"],
        "plan_url": artifact_urls["plan_url"],
        "log_url": artifact_urls["log_url"],
        "summary": summary,
        "error": db_job.error_message or None,
    }
                
    return response_data


@app.get("/api/v1/jobs/{job_id}/summary", response_model=JobSummaryResponse, tags=["Jobs"])
async def get_job_summary(
    job_id: str,
    service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
    """Return compact, machine-readable job diagnostics summary."""
    db_job = _get_owned_job_or_404(job_id, service, current_user)
    summary = service.extract_job_summary(db_job)
    if not summary:
        raise HTTPException(status_code=404, detail="Job summary not available")
    return summary


@app.get("/api/v1/jobs/{job_id}/video", tags=["Jobs"])
async def get_job_video(
    job_id: str,
    service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
    """Serve video with quality hardening: anti-caching, no-store for security."""
    db_job = _get_owned_job_or_404(job_id, service, current_user)
    if db_job.video_path and (db_job.video_path.startswith("s3://") or db_job.video_path.startswith("cloudinary://")):
        if not cloud_storage:
            raise HTTPException(status_code=503, detail="Cloud storage backend unavailable")
        try:
            signed_url = cloud_storage.generate_signed_url(db_job.video_path, expires_in=3600)
        except Exception:
            raise HTTPException(status_code=503, detail="Failed to generate cloud artifact URL")
        return RedirectResponse(url=signed_url, status_code=307)

    path = _job_video_path(db_job)
    if not path:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Video quality hardening: prevent caching of premium content
    # This ensures videos can't be cached on proxies/CDN and leaked
    response = FileResponse(
        path, 
        media_type="video/mp4", 
        filename=f"phiversity-{job_id}.mp4"
    )
    
    # Anti-caching headers for commercial security
    # Videos must not be cached to prevent unauthorized access
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    # Prevent clickjacking - videos should not be embeddable on unauthorized sites
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # For free tier: indicate watermarked content (watermark applied during generation)
    if current_user.quality_tier == QualityTier.FREE:
        response.headers["X-Content-Quality"] = "watermarked"
    else:
        response.headers["X-Content-Quality"] = current_user.quality_tier.value
    
    return response


@app.get("/api/v1/jobs/{job_id}/plan", tags=["Jobs"])
async def get_job_plan(
    job_id: str,
    service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
    """Serve plan with quality hardening: anti-caching headers."""
    db_job = _get_owned_job_or_404(job_id, service, current_user)
    if db_job.plan_path and (db_job.plan_path.startswith("s3://") or db_job.plan_path.startswith("cloudinary://")):
        if not cloud_storage:
            raise HTTPException(status_code=503, detail="Cloud storage backend unavailable")
        try:
            signed_url = cloud_storage.generate_signed_url(db_job.plan_path, expires_in=3600)
        except Exception:
            raise HTTPException(status_code=503, detail="Failed to generate cloud artifact URL")
        return RedirectResponse(url=signed_url, status_code=307)

    path = _job_plan_path(db_job)
    if not path:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    response = FileResponse(path, media_type="application/json", filename=f"phiversity-plan-{job_id}.json")
    # Anti-caching for security
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/api/v1/jobs/{job_id}/log", tags=["Jobs"])
async def get_job_log(
    job_id: str,
    service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
    """Serve log with quality hardening: anti-caching headers."""
    db_job = _get_owned_job_or_404(job_id, service, current_user)
    path = _job_log_path(db_job)
    if not path:
        raise HTTPException(status_code=404, detail="Log not found")
    
    response = FileResponse(path, media_type="text/plain; charset=utf-8", filename=f"phiversity-log-{job_id}.txt")
    # Anti-caching for security
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# --- Legacy Redirects ---

@app.post("/api/run", tags=["Legacy"])
async def legacy_run(
    req: RunRequest,
    service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
    job = service.create_job()
    job.user_id = current_user.id
    if req.idempotency_key:
        job.idempotency_key = _scoped_idempotency_key(current_user.id, req.idempotency_key)
    service.db.commit()
    service.start_background_job(job.id, req.model_dump())
    return {"job_id": job.id, "status": "queued"}


@app.get("/api/jobs/{job_id}", tags=["Legacy"])
async def legacy_job_status(
    job_id: str,
    service: JobService = Depends(get_job_service),
    current_user: User = Depends(get_current_user)
):
    return await get_job_status(job_id, service, current_user)

# --- Static Mounts ---

app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
