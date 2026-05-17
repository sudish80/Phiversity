import os
import logging
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase


logger = logging.getLogger(__name__)

# Define the local database path
ROOT = Path(__file__).resolve().parents[2]
DB_DIR = ROOT / "media" / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)

def _normalize_database_url(database_url: str) -> str:
    # Many platforms expose postgres://, but SQLAlchemy expects postgresql://
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


SQLALCHEMY_DATABASE_URL = _normalize_database_url(
    os.getenv("DATABASE_URL", f"sqlite:///{DB_DIR}/phiversity.db")
)

REQUIRED_SCHEMA = {
    "users": {
        "id",
        "email",
        "hashed_password",
        "password_hash_scheme",
        "password_hash_updated_at",
        "is_active",
        "email_verified",
        "email_verified_at",
        "role",
        "quality_tier",
        "watermark_enabled",
        "password_changed_at",
        "failed_login_attempts",
        "locked_until",
        "mfa_enabled",
        "mfa_secret_encrypted",
        "mfa_backup_codes_encrypted",
        "last_login_ip",
        "last_login_at",
        "created_at",
    },
    "jobs": {
        "id",
        "status",
        "progress",
        "request_payload",
        "attempt_count",
        "worker_id",
        "claimed_at",
        "started_at",
        "finished_at",
        "lease_expires_at",
        "video_path",
        "video_url",
        "plan_path",
        "plan_url",
        "log_path",
        "log_url",
        "out_dir",
        "log",
        "user_id",
        "idempotency_key",
        "created_at",
        "updated_at",
    },
    "password_reset_tokens": {
        "id",
        "user_id",
        "token_hash",
        "expires_at",
        "used_at",
        "created_at",
        "requested_ip",
    },
    "refresh_tokens": {
        "id",
        "user_id",
        "token_hash",
        "family_id",
        "parent_token_id",
        "expires_at",
        "revoked_at",
        "revoked_reason",
        "rotated_to_id",
        "created_at",
        "created_ip",
        "created_user_agent",
    },
    "revoked_access_tokens": {
        "id",
        "jti",
        "user_id",
        "expires_at",
        "revoked_at",
        "reason",
    },
    "audit_logs": {
        "id",
        "user_id",
        "event_type",
        "status",
        "description",
        "client_ip",
        "user_agent",
        "request_path",
        "request_method",
        "response_status",
        "error_message",
        "metadata",
        "created_at",
    },
    "login_attempts": {
        "id",
        "user_id",
        "email",
        "success",
        "client_ip",
        "user_agent",
        "created_at",
    },
    "email_verification_tokens": {
        "id",
        "user_id",
        "token_hash",
        "expires_at",
        "verified_at",
        "created_at",
        "requested_ip",
    },
    "api_keys": {
        "id",
        "user_id",
        "name",
        "key_prefix",
        "key_hash",
        "scopes",
        "is_active",
        "expires_at",
        "last_used_at",
        "revoked_at",
        "created_at",
    },
    "security_events": {
        "id",
        "user_id",
        "event_type",
        "severity",
        "source",
        "description",
        "client_ip",
        "metadata",
        "notified_at",
        "created_at",
    },
    "passwordless_login_tokens": {
        "id",
        "user_id",
        "token_hash",
        "expires_at",
        "used_at",
        "requested_ip",
        "created_at",
    },
    "oauth_clients": {
        "id",
        "name",
        "client_id",
        "client_secret_hash",
        "redirect_uris",
        "scopes",
        "grants",
        "is_active",
        "created_at",
    },
    "oauth_authorization_codes": {
        "id",
        "client_id",
        "user_id",
        "code_hash",
        "redirect_uri",
        "scope",
        "code_challenge",
        "code_challenge_method",
        "expires_at",
        "used_at",
        "created_at",
    },
    "webauthn_credentials": {
        "id",
        "user_id",
        "credential_id",
        "public_key",
        "sign_count",
        "aaguid",
        "transports",
        "created_at",
        "last_used_at",
    },
    "saml_identity_providers": {
        "id",
        "name",
        "entity_id",
        "sso_url",
        "x509_cert",
        "acs_url",
        "is_active",
        "created_at",
    },
    "auth_identities": {
        "id",
        "user_id",
        "provider",
        "provider_user_id",
        "provider_email",
        "is_primary",
        "is_verified",
        "linked_at",
        "last_used_at",
    },
    "user_profiles": {
        "id",
        "user_id",
        "username",
        "full_name",
        "phone_number",
        "signup_source",
        "signup_ip",
        "signup_user_agent",
        "created_at",
        "updated_at",
    },
    "payment_accounts": {
        "id",
        "user_id",
        "provider",
        "provider_customer_id",
        "email",
        "default_payment_method",
        "is_active",
        "created_at",
        "updated_at",
    },
    "subscriptions": {
        "id",
        "user_id",
        "payment_account_id",
        "provider",
        "provider_subscription_id",
        "tier",
        "status",
        "currency",
        "amount_cents",
        "interval",
        "period_start",
        "period_end",
        "cancel_at_period_end",
        "tenant_id",
        "metadata_json",
        "created_at",
        "updated_at",
    },
    "payment_invoices": {
        "id",
        "user_id",
        "subscription_id",
        "provider",
        "provider_invoice_id",
        "status",
        "amount_due_cents",
        "amount_paid_cents",
        "currency",
        "hosted_invoice_url",
        "invoice_pdf_url",
        "due_at",
        "paid_at",
        "metadata_json",
        "created_at",
    },
    "payment_transactions": {
        "id",
        "user_id",
        "subscription_id",
        "invoice_id",
        "provider",
        "provider_payment_id",
        "event_type",
        "status",
        "amount_cents",
        "currency",
        "payment_method",
        "failure_code",
        "failure_message",
        "metadata_json",
        "occurred_at",
        "created_at",
    },
}


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _is_production_like_env() -> bool:
    env_name = (
        os.getenv("PHIVERSITY_ENV")
        or os.getenv("APP_ENV")
        or os.getenv("ENVIRONMENT")
        or ""
    ).strip().lower()
    return env_name in {"prod", "production", "staging"}


def _guard_database_url(database_url: str) -> None:
    sqlite_url = database_url.startswith("sqlite")
    allow_sqlite = _is_truthy(os.getenv("ALLOW_SQLITE_IN_PRODUCTION"))
    require_server_db = _is_truthy(os.getenv("REQUIRE_SERVER_DB")) or _is_production_like_env()

    if sqlite_url and require_server_db and not allow_sqlite:
        raise RuntimeError(
            "SQLite is disabled in production-like environments. "
            "Set DATABASE_URL to a server database (for example PostgreSQL), "
            "or explicitly set ALLOW_SQLITE_IN_PRODUCTION=true for local-only testing."
        )


def schema_readiness_required() -> bool:
    return _is_truthy(os.getenv("REQUIRE_DB_MIGRATIONS")) or _is_production_like_env()


def missing_required_schema(engine_to_check) -> list[str]:
    inspector = inspect(engine_to_check)
    table_names = set(inspector.get_table_names())
    missing: list[str] = []

    if schema_readiness_required() and "alembic_version" not in table_names:
        missing.append("missing table 'alembic_version'")

    for table_name, required_columns in REQUIRED_SCHEMA.items():
        if table_name not in table_names:
            missing.append(f"missing table '{table_name}'")
            continue
        existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
        for column_name in sorted(required_columns - existing_columns):
            missing.append(f"missing column '{table_name}.{column_name}'")

    return missing


def ensure_required_schema_ready(engine_to_check) -> None:
    if not schema_readiness_required():
        return

    missing = missing_required_schema(engine_to_check)
    if missing:
        details = "\n".join(f"- {item}" for item in missing)
        raise RuntimeError(
            "Database schema is not ready for this application version. "
            "Run Alembic migrations before starting the service.\n"
            f"{details}"
        )


_guard_database_url(SQLALCHEMY_DATABASE_URL)

# Create Database Engine with optimizations
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

# Query optimization settings
engine_options = {}
if not SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # Connection pooling for production databases
    engine_options = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,  # Verify connections before use
        "pool_recycle": 300,  # Recycle connections after 5 minutes
    }

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args=connect_args,
    **engine_options
)


def _verify_database_connectivity(engine_to_check) -> None:
    # Fail fast so invalid credentials or unreachable DBs do not surface later mid-request.
    with engine_to_check.connect() as connection:
        connection.execute(text("SELECT 1"))


_verify_database_connectivity(engine)
logger.info("Database connection verified")

# Session Local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
class Base(DeclarativeBase):
    pass

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
