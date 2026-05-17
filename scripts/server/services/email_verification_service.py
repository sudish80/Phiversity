"""
Email verification service for account confirmation flow.
Generates and validates one-time email verification tokens.
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session

from ..models import User, EmailVerificationToken


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


class EmailVerificationService:
    """Service for managing email verification tokens and status."""

    def __init__(self, db: Session):
        self.db = db

    def create_verification_token(
        self,
        user: User,
        ttl_hours: int = 24,
        requested_ip: Optional[str] = None,
    ) -> str:
        """
        Create a one-time email verification token for a user.

        Args:
            user: User to verify email for
            ttl_hours: Token expiration time in hours (default 24)
            requested_ip: IP address that requested the token

        Returns:
            Raw token string (should be sent via email)
        """
        raw_token = secrets.token_urlsafe(32)

        token = EmailVerificationToken(
            user_id=user.id,
            token_hash=_hash_token(raw_token),
            expires_at=_utc_now() + timedelta(hours=ttl_hours),
            requested_ip=requested_ip,
        )
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)

        return raw_token

    def verify_email_token(
        self,
        user_id: int,
        token: str,
    ) -> bool:
        """
        Verify an email token and mark user's email as verified.

        Args:
            user_id: User ID to verify
            token: Raw token string from email

        Returns:
            True if verification successful, False if token invalid/expired
        """
        token_hash = _hash_token(token)

        # Find the token
        db_token = (
            self.db.query(EmailVerificationToken)
            .filter(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.token_hash == token_hash,
            )
            .first()
        )

        if not db_token:
            return False

        # Check if expired
        if db_token.expires_at < _utc_now():
            return False

        # Check if already verified
        if db_token.verified_at is not None:
            return False

        # Mark token as verified
        db_token.verified_at = _utc_now()
        self.db.add(db_token)

        # Mark user's email as verified
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.email_verified = True
            user.email_verified_at = _utc_now()
            self.db.add(user)

        self.db.commit()
        return True

    def is_email_verified(self, user: User) -> bool:
        """Check if user's email is verified."""
        return user.email_verified is True

    def get_pending_verification_token(
        self,
        user_id: int,
    ) -> Optional[EmailVerificationToken]:
        """Get pending (unverified) email verification token for user."""
        return (
            self.db.query(EmailVerificationToken)
            .filter(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.verified_at.is_(None),
                EmailVerificationToken.expires_at > _utc_now(),
            )
            .first()
        )

    def resend_verification_token(
        self,
        user: User,
        requested_ip: Optional[str] = None,
    ) -> str:
        """
        Generate a new verification token, invalidating old ones.

        Args:
            user: User to generate token for
            requested_ip: IP address requesting the resend

        Returns:
            New raw token string
        """
        # Mark all existing tokens as expired
        self.db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.verified_at.is_(None),
        ).update(
            {EmailVerificationToken.expires_at: datetime.now(timezone.utc)},
            synchronize_session=False,
        )
        self.db.commit()

        # Create new token
        return self.create_verification_token(user, requested_ip=requested_ip)

    def cleanup_expired_tokens(self, retention_days: int = 7) -> int:
        """
        Delete old email verification tokens.

        Args:
            retention_days: How long to keep expired tokens

        Returns:
            Number of deleted tokens
        """
        cutoff_date = _utc_now() - timedelta(days=retention_days)

        deleted = self.db.query(EmailVerificationToken).filter(
            EmailVerificationToken.expires_at < cutoff_date
        ).delete(synchronize_session=False)

        self.db.commit()
        return deleted
