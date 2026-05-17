import hashlib
import secrets
import uuid
from datetime import timedelta
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models import (
    User,
    UserRole,
    PasswordResetToken,
    RefreshToken,
    RevokedAccessToken,
    AuditLog,
    LoginAttempt,
    AuthIdentity,
    UserProfile,
)
from ..auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    DEFAULT_USER_SCOPES,
    ADMIN_SCOPES,
    get_password_hash_scheme,
    password_hash_needs_upgrade,
)
from .base import BaseService
from typing import Optional, List


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_utc_naive(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

class UserService(BaseService):
    @staticmethod
    def _normalize_email(email: str) -> str:
        return (email or "").strip().lower()

    @staticmethod
    def _normalize_username(username: Optional[str]) -> Optional[str]:
        candidate = (username or "").strip().lower()
        return candidate or None

    def create_user(
        self,
        email: str,
        password: str,
        role: UserRole = UserRole.USER,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        signup_source: str = "email",
        signup_ip: Optional[str] = None,
        signup_user_agent: Optional[str] = None,
    ) -> User:
        normalized_email = self._normalize_email(email)
        if not normalized_email:
            raise ValueError("Email is required")

        existing = self.get_user_by_email(normalized_email)
        if existing:
            raise ValueError("Email already registered")

        normalized_username = self._normalize_username(username)
        if normalized_username:
            existing_username = (
                self.db.query(UserProfile)
                .filter(func.lower(UserProfile.username) == normalized_username)
                .first()
            )
            if existing_username:
                raise ValueError("Username already taken")

        hashed_password = get_password_hash(password)
        user = User(
            email=normalized_email,
            hashed_password=hashed_password,
            password_hash_scheme=get_password_hash_scheme(),
            password_hash_updated_at=_utc_now(),
            role=role,
        )
        self.db.add(user)

        local_identity = AuthIdentity(
            user=user,
            provider="local",
            provider_user_id=normalized_email,
            provider_email=normalized_email,
            is_primary=True,
            is_verified=False,
        )
        self.db.add(local_identity)

        profile = UserProfile(
            user=user,
            username=normalized_username,
            full_name=(full_name or "").strip() or None,
            phone_number=(phone_number or "").strip() or None,
            signup_source=(signup_source or "email").strip().lower() or "email",
            signup_ip=signup_ip,
            signup_user_agent=signup_user_agent,
        )
        self.db.add(profile)

        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        normalized_email = self._normalize_email(email)
        if not normalized_email:
            return None
        return (
            self.db.query(User)
            .filter(func.lower(User.email) == normalized_email)
            .first()
        )

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None

        # Seamlessly upgrade legacy password hashes after successful login.
        if password_hash_needs_upgrade(user.hashed_password):
            user.hashed_password = get_password_hash(password)
            user.password_hash_scheme = get_password_hash_scheme()
            user.password_hash_updated_at = _utc_now()
            self.db.commit()
            self.db.refresh(user)
        return user

    def issue_session_tokens(
        self,
        user: User,
        access_ttl: timedelta = timedelta(minutes=30),
        refresh_ttl: timedelta = timedelta(days=30),
        family_id: Optional[str] = None,
        parent_refresh_id: Optional[int] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> dict:
        # Determine scopes based on user role
        scopes = ADMIN_SCOPES if user.role == UserRole.ADMIN else DEFAULT_USER_SCOPES
        
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_ttl,
            scopes=scopes,
        )

        raw_refresh = secrets.token_urlsafe(64)
        refresh = RefreshToken(
            user_id=user.id,
            token_hash=_hash_token(raw_refresh),
            family_id=family_id or uuid.uuid4().hex,
            parent_token_id=parent_refresh_id,
            expires_at=_utc_now() + refresh_ttl,
            created_ip=ip,
            created_user_agent=user_agent,
        )
        self.db.add(refresh)
        self.db.commit()
        self.db.refresh(refresh)

        return {
            "access_token": access_token,
            "refresh_token": raw_refresh,
            "token_type": "bearer",
            "refresh_expires_at": refresh.expires_at,
            "user_id": user.id,  # Include user_id in response for audit logging
        }

    def _get_refresh_by_raw(self, raw_refresh_token: str) -> Optional[RefreshToken]:
        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == _hash_token(raw_refresh_token))
            .first()
        )

    def rotate_refresh_token(
        self,
        raw_refresh_token: str,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[dict]:
        current = self._get_refresh_by_raw(raw_refresh_token)
        now = _utc_now().replace(tzinfo=None)
        if not current:
            return None
        if current.revoked_at is not None:
            return None
        if _to_utc_naive(current.expires_at) <= now:
            return None

        user = self.db.query(User).filter(User.id == current.user_id).first()
        if not user:
            return None

        issued = self.issue_session_tokens(
            user=user,
            family_id=current.family_id,
            parent_refresh_id=current.id,
            ip=ip,
            user_agent=user_agent,
        )
        new_db_refresh = self._get_refresh_by_raw(issued["refresh_token"])
        current.revoked_at = now
        current.revoked_reason = "rotated"
        if new_db_refresh:
            current.rotated_to_id = new_db_refresh.id
        self.db.commit()
        return issued

    def revoke_refresh_token(self, raw_refresh_token: str, reason: str = "user_logout") -> bool:
        token = self._get_refresh_by_raw(raw_refresh_token)
        if not token:
            return False
        if token.revoked_at is None:
            token.revoked_at = _utc_now()
            token.revoked_reason = reason
            self.db.commit()
        return True

    def revoke_refresh_family(self, family_id: str, reason: str = "family_revoked") -> int:
        now = _utc_now()
        rows = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
            .all()
        )
        for row in rows:
            row.revoked_at = now
            row.revoked_reason = reason
        self.db.commit()
        return len(rows)

    def revoke_all_user_refresh_tokens(self, user_id: int, reason: str) -> int:
        now = _utc_now()
        rows = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .all()
        )
        for row in rows:
            row.revoked_at = now
            row.revoked_reason = reason
        self.db.commit()
        return len(rows)

    def revoke_access_jti(self, jti: str, user_id: Optional[int], expires_at: datetime, reason: str) -> None:
        exists = self.db.query(RevokedAccessToken).filter(RevokedAccessToken.jti == jti).first()
        if exists:
            return
        revoked = RevokedAccessToken(
            jti=jti,
            user_id=user_id,
            expires_at=expires_at,
            reason=reason,
        )
        self.db.add(revoked)
        self.db.commit()

    def create_password_reset_token(self, user: User, requested_ip: Optional[str] = None) -> str:
        raw_token = secrets.token_urlsafe(48)
        token = PasswordResetToken(
            user_id=user.id,
            token_hash=_hash_token(raw_token),
            expires_at=_utc_now() + timedelta(minutes=30),
            requested_ip=requested_ip,
        )
        self.db.add(token)
        self.db.commit()
        return raw_token

    def consume_password_reset_token(self, raw_token: str, new_password: str) -> bool:
        now = _utc_now().replace(tzinfo=None)
        token = (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == _hash_token(raw_token))
            .first()
        )
        if not token:
            return False
        if token.used_at is not None:
            return False
        if _to_utc_naive(token.expires_at) <= now:
            return False

        user = self.db.query(User).filter(User.id == token.user_id).first()
        if not user:
            return False

        user.hashed_password = get_password_hash(new_password)
        user.password_hash_scheme = get_password_hash_scheme()
        user.password_hash_updated_at = _utc_now()
        used_updated = (
            self.db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.id == token.id,
                PasswordResetToken.used_at.is_(None),
            )
            .update({"used_at": now}, synchronize_session=False)
        )
        if used_updated != 1:
            self.db.rollback()
            return False
        self.db.commit()

        self.revoke_all_user_refresh_tokens(user.id, reason="password_reset")
        return True

    def cleanup_expired_auth_records(self, revoked_retention_seconds: int = 86400) -> dict:
        now_naive = _utc_now().replace(tzinfo=None)
        revoked_cutoff_naive = (_utc_now() - timedelta(seconds=max(0, revoked_retention_seconds))).replace(tzinfo=None)

        deleted_reset = (
            self.db.query(PasswordResetToken)
            .filter(
                (PasswordResetToken.used_at.isnot(None)) |
                (PasswordResetToken.expires_at < now_naive)
            )
            .delete(synchronize_session=False)
        )

        deleted_refresh = (
            self.db.query(RefreshToken)
            .filter(
                (RefreshToken.expires_at < now_naive) |
                (
                    RefreshToken.revoked_at.isnot(None) &
                    (RefreshToken.revoked_at < revoked_cutoff_naive)
                )
            )
            .delete(synchronize_session=False)
        )

        deleted_revoked_access = (
            self.db.query(RevokedAccessToken)
            .filter(RevokedAccessToken.expires_at < now_naive)
            .delete(synchronize_session=False)
        )

        self.db.commit()
        return {
            "password_reset_tokens": int(deleted_reset or 0),
            "refresh_tokens": int(deleted_refresh or 0),
            "revoked_access_tokens": int(deleted_revoked_access or 0),
        }

    # --- Account Lockout Management ---
    
    def record_login_attempt(
        self,
        email: str,
        success: bool,
        user_id: Optional[int] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> LoginAttempt:
        """Record a login attempt for tracking failed attempts and account lockout."""
        attempt = LoginAttempt(
            user_id=user_id,
            email=self._normalize_email(email),
            success=success,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def get_latest_failed_attempts(
        self,
        email: str,
        within_minutes: int = 15,
        limit: int = 10,
    ) -> list[LoginAttempt]:
        """Get recent failed login attempts within a time window."""
        normalized_email = self._normalize_email(email)
        cutoff_time = _utc_now() - timedelta(minutes=within_minutes)
        
        return (
            self.db.query(LoginAttempt)
            .filter(
                LoginAttempt.email == normalized_email,
                LoginAttempt.success == False,
                LoginAttempt.created_at > cutoff_time,
            )
            .order_by(LoginAttempt.created_at.desc())
            .limit(limit)
            .all()
        )

    def is_account_locked(
        self,
        email: str,
        max_attempts: int = 5,
        lockout_minutes: int = 15,
    ) -> bool:
        """Check if an account is currently locked due to too many failed attempts."""
        failed_attempts = self.get_latest_failed_attempts(
            email,
            within_minutes=lockout_minutes,
            limit=max_attempts,
        )
        return len(failed_attempts) >= max_attempts

    def unlock_account(self, email: str) -> bool:
        """Manually unlock an account (for admin use or after timeout)."""
        normalized_email = self._normalize_email(email)
        user = self.get_user_by_email(normalized_email)
        if not user:
            return False
        
        # Delete all failed login attempts for this email
        self.db.query(LoginAttempt).filter(
            LoginAttempt.email == normalized_email,
            LoginAttempt.success == False,
        ).delete(synchronize_session=False)
        
        self.db.commit()
        return True

    def cleanup_old_login_attempts(
        self,
        retention_days: int = 90,
    ) -> int:
        """Delete old login attempt records."""
        cutoff_date = _utc_now() - timedelta(days=retention_days)
        deleted = self.db.query(LoginAttempt).filter(
            LoginAttempt.created_at < cutoff_date
        ).delete(synchronize_session=False)
        self.db.commit()
        return deleted
