import enum
import uuid
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, Boolean, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class QualityTier(enum.Enum):
    """Video quality tiers for commercial use access control"""
    FREE = "free"         # Low quality (480p), watermarked
    STANDARD = "standard" # Medium quality (720p)
    PREMIUM = "premium"    # High quality (1080p)
    ENTERPRISE = "enterprise"  # Original quality, no restrictions

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index('ix_users_email_lower', 'email', unique=True, postgresql_where=Column('email')),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(254), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    password_hash_scheme = Column(String(32), nullable=False, default="argon2")
    password_hash_updated_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    email_verified = Column(Boolean, default=False, index=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, index=True)
    quality_tier = Column(Enum(QualityTier), default=QualityTier.FREE, index=True)
    watermark_enabled = Column(Boolean, default=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True, index=True)
    mfa_enabled = Column(Boolean, default=False, index=True)
    mfa_secret_encrypted = Column(Text, nullable=True)
    mfa_backup_codes_encrypted = Column(Text, nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 compatible
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships with cascade delete
    jobs = relationship("JobModel", back_populates="user", cascade="all, delete-orphan")
    password_history = relationship("PasswordHistory", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    login_attempts = relationship("LoginAttempt", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    auth_identities = relationship("AuthIdentity", back_populates="user", cascade="all, delete-orphan")
    payment_accounts = relationship("PaymentAccount", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payment_invoices = relationship("PaymentInvoice", back_populates="user", cascade="all, delete-orphan")
    payment_transactions = relationship("PaymentTransaction", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = (
        UniqueConstraint("username", name="uq_user_profiles_username"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    username = Column(String(64), nullable=True, index=True)
    full_name = Column(String(120), nullable=True)
    phone_number = Column(String(32), nullable=True)
    signup_source = Column(String(32), nullable=False, default="email", index=True)
    signup_ip = Column(String(45), nullable=True)
    signup_user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")

class JobModel(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        Index('ix_jobs_user_status', 'user_id', 'status'),
        Index('ix_jobs_status_created', 'status', 'created_at'),
    )

    id = Column(String(12), primary_key=True, index=True, default=lambda: uuid.uuid4().hex[:12])
    status = Column(String(20), default="queued", index=True)
    progress = Column(Integer, default=0)
    request_payload = Column(Text, nullable=True)
    attempt_count = Column(Integer, default=0)
    worker_id = Column(String(64), nullable=True, index=True)
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    lease_expires_at = Column(DateTime(timezone=True), nullable=True)
    video_path = Column(String(512), nullable=True)
    video_url = Column(String(512), nullable=True)
    plan_path = Column(String(512), nullable=True)
    plan_url = Column(String(512), nullable=True)
    log_path = Column(String(512), nullable=True)
    log_url = Column(String(512), nullable=True)
    out_dir = Column(String(512), nullable=True)
    log = Column(Text, default="")
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    idempotency_key = Column(String(128), nullable=True, index=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="jobs")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = (
        Index('ix_pw_reset_user_expires', 'user_id', 'expires_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    requested_ip = Column(String(45), nullable=True)
    
    # Relationship
    user = relationship("User")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index('ix_refresh_user_expires', 'user_id', 'expires_at'),
        Index('ix_refresh_family', 'family_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True, index=True)
    family_id = Column(String(32), nullable=False, index=True)
    parent_token_id = Column(Integer, ForeignKey("refresh_tokens.id"), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_reason = Column(String(50), nullable=True)
    rotated_to_id = Column(Integer, ForeignKey("refresh_tokens.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_ip = Column(String(45), nullable=True)
    created_user_agent = Column(String(255), nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="refresh_tokens")


class RevokedAccessToken(Base):
    __tablename__ = "revoked_access_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    reason = Column(String, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    event_type = Column(String, nullable=False, index=True)  # login, logout, password_reset, token_refresh, signup, etc.
    status = Column(String, nullable=False)  # success, failure
    description = Column(String, nullable=True)
    client_ip = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    request_path = Column(String, nullable=True)
    request_method = Column(String, nullable=True)
    response_status = Column(Integer, nullable=True)
    error_message = Column(String, nullable=True)
    audit_metadata = Column("metadata", Text, key="audit_metadata", nullable=True)  # JSON string for additional context
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship
    user = relationship("User", back_populates="audit_logs")


class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    __table_args__ = (
        Index('ix_login_attempt_email_created', 'email', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    email = Column(String(254), nullable=False, index=True)
    success = Column(Boolean, default=False, index=True)
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationship
    user = relationship("User", back_populates="login_attempts")


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)  # NULL if not yet verified
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    requested_ip = Column(String, nullable=True)


class PasswordHistory(Base):
    """Track password history to prevent reuse."""
    __tablename__ = "password_history"
    __table_args__ = (
        Index('ix_pw_history_user_created', 'user_id', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationship
    user = relationship("User", back_populates="password_history")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    key_prefix = Column(String, nullable=False, index=True)
    key_hash = Column(String, nullable=False, unique=True, index=True)
    scopes = Column(Text, nullable=False, default="[]")
    is_active = Column(Boolean, default=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    severity = Column(String, nullable=False, index=True)  # low|medium|high|critical
    source = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    client_ip = Column(String, nullable=True, index=True)
    event_metadata = Column("metadata", Text, key="event_metadata", nullable=True)
    notified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class PasswordlessLoginToken(Base):
    __tablename__ = "passwordless_login_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    requested_ip = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class OAuthClient(Base):
    __tablename__ = "oauth_clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    client_id = Column(String, nullable=False, unique=True, index=True)
    client_secret_hash = Column(String, nullable=False)
    redirect_uris = Column(Text, nullable=False, default="[]")
    scopes = Column(Text, nullable=False, default="[]")
    grants = Column(Text, nullable=False, default="[]")
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class OAuthAuthorizationCode(Base):
    __tablename__ = "oauth_authorization_codes"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    code_hash = Column(String, nullable=False, unique=True, index=True)
    redirect_uri = Column(Text, nullable=False)
    scope = Column(Text, nullable=True)
    code_challenge = Column(String, nullable=True)
    code_challenge_method = Column(String, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class WebAuthnCredential(Base):
    __tablename__ = "webauthn_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    credential_id = Column(String, nullable=False, unique=True, index=True)
    public_key = Column(Text, nullable=False)
    sign_count = Column(Integer, default=0)
    aaguid = Column(String, nullable=True)
    transports = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)


class SAMLIdentityProvider(Base):
    __tablename__ = "saml_identity_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    sso_url = Column(String, nullable=False)
    x509_cert = Column(Text, nullable=False)
    acs_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class AuthIdentity(Base):
    __tablename__ = "auth_identities"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_auth_identities_provider_user"),
        UniqueConstraint("provider", "provider_email", name="uq_auth_identities_provider_email"),
        Index("ix_auth_identities_user_provider", "user_id", "provider"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(32), nullable=False, index=True)  # local|google|facebook|saml|oauth|webauthn
    provider_user_id = Column(String(255), nullable=False, index=True)
    provider_email = Column(String(254), nullable=True, index=True)
    is_primary = Column(Boolean, default=False, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    linked_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="auth_identities")


class PaymentAccount(Base):
    __tablename__ = "payment_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_customer_id", name="uq_payment_accounts_provider_customer"),
        Index("ix_payment_accounts_user_provider", "user_id", "provider"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(32), nullable=False, index=True)  # stripe|paypal
    provider_customer_id = Column(String(255), nullable=False, index=True)
    email = Column(String(254), nullable=True, index=True)
    default_payment_method = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="payment_accounts")


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("provider", "provider_subscription_id", name="uq_subscriptions_provider_sub_id"),
        Index("ix_subscriptions_user_status", "user_id", "status"),
        Index("ix_subscriptions_tenant", "tenant_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_account_id = Column(Integer, ForeignKey("payment_accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    provider = Column(String(32), nullable=False, index=True)
    provider_subscription_id = Column(String(255), nullable=False, index=True)
    tier = Column(String(32), nullable=False, index=True)  # free|standard|premium|enterprise
    status = Column(String(32), nullable=False, default="active", index=True)  # active|trialing|past_due|canceled
    currency = Column(String(8), nullable=False, default="USD")
    amount_cents = Column(Integer, nullable=False, default=0)
    interval = Column(String(16), nullable=False, default="month")  # month|year
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    tenant_id = Column(String(64), nullable=True, index=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="subscriptions")


class PaymentInvoice(Base):
    __tablename__ = "payment_invoices"
    __table_args__ = (
        UniqueConstraint("provider", "provider_invoice_id", name="uq_payment_invoices_provider_invoice"),
        Index("ix_payment_invoices_user_status", "user_id", "status"),
        Index("ix_payment_invoices_subscription", "subscription_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True, index=True)
    provider = Column(String(32), nullable=False, index=True)
    provider_invoice_id = Column(String(255), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="open", index=True)  # open|paid|void|uncollectible
    amount_due_cents = Column(Integer, nullable=False, default=0)
    amount_paid_cents = Column(Integer, nullable=False, default=0)
    currency = Column(String(8), nullable=False, default="USD")
    hosted_invoice_url = Column(String(1024), nullable=True)
    invoice_pdf_url = Column(String(1024), nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="payment_invoices")


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    __table_args__ = (
        UniqueConstraint("provider", "provider_payment_id", name="uq_payment_transactions_provider_payment"),
        Index("ix_payment_transactions_user_status", "user_id", "status"),
        Index("ix_payment_transactions_invoice", "invoice_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True, index=True)
    invoice_id = Column(Integer, ForeignKey("payment_invoices.id", ondelete="SET NULL"), nullable=True, index=True)
    provider = Column(String(32), nullable=False, index=True)
    provider_payment_id = Column(String(255), nullable=False, index=True)
    event_type = Column(String(64), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="succeeded", index=True)  # succeeded|pending|failed|refunded
    amount_cents = Column(Integer, nullable=False, default=0)
    currency = Column(String(8), nullable=False, default="USD")
    payment_method = Column(String(64), nullable=True)
    failure_code = Column(String(64), nullable=True)
    failure_message = Column(String(255), nullable=True)
    metadata_json = Column(Text, nullable=True)
    occurred_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="payment_transactions")
