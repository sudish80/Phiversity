"""Passwordless authentication service using one-time magic-link style tokens."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from ..models import PasswordlessLoginToken, User


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


class PasswordlessService:
    def __init__(self, db: Session):
        self.db = db

    def create_token(self, user: User, ttl_minutes: int = 15, requested_ip: Optional[str] = None) -> str:
        raw_token = secrets.token_urlsafe(48)
        row = PasswordlessLoginToken(
            user_id=user.id,
            token_hash=_hash_token(raw_token),
            expires_at=_utc_now() + timedelta(minutes=ttl_minutes),
            requested_ip=requested_ip,
        )
        self.db.add(row)
        self.db.commit()
        return raw_token

    def consume_token(self, raw_token: str) -> Optional[User]:
        now = _utc_now().replace(tzinfo=None)
        row = (
            self.db.query(PasswordlessLoginToken)
            .filter(PasswordlessLoginToken.token_hash == _hash_token(raw_token))
            .first()
        )
        if not row:
            return None
        if row.used_at is not None:
            return None
        expires_at = row.expires_at.replace(tzinfo=None) if row.expires_at.tzinfo else row.expires_at
        if expires_at <= now:
            return None

        user = self.db.query(User).filter(User.id == row.user_id).first()
        if not user:
            return None

        row.used_at = _utc_now()
        self.db.commit()
        return user

    def cleanup_expired(self, retention_days: int = 7) -> int:
        cutoff = _utc_now() - timedelta(days=retention_days)
        deleted = (
            self.db.query(PasswordlessLoginToken)
            .filter(PasswordlessLoginToken.expires_at < cutoff)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return int(deleted or 0)
