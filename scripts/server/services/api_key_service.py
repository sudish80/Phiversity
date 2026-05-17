"""API key creation, verification, and lifecycle management."""

import hashlib
import json
import secrets
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session

from ..models import APIKey


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


class APIKeyService:
    def __init__(self, db: Session):
        self.db = db

    def create_key(
        self,
        user_id: int,
        name: str,
        scopes: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None,
    ) -> Tuple[str, APIKey]:
        raw_key = f"pk_live_{secrets.token_urlsafe(36)}"
        key_hash = _hash_key(raw_key)
        prefix = raw_key[:12]

        row = APIKey(
            user_id=user_id,
            name=name,
            key_prefix=prefix,
            key_hash=key_hash,
            scopes=json.dumps(scopes or []),
            expires_at=expires_at,
            is_active=True,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return raw_key, row

    def list_keys(self, user_id: int) -> List[APIKey]:
        return (
            self.db.query(APIKey)
            .filter(APIKey.user_id == user_id)
            .order_by(APIKey.created_at.desc())
            .all()
        )

    def revoke_key(self, user_id: int, key_id: int) -> bool:
        row = (
            self.db.query(APIKey)
            .filter(APIKey.id == key_id, APIKey.user_id == user_id)
            .first()
        )
        if not row:
            return False
        row.is_active = False
        row.revoked_at = _utc_now()
        self.db.commit()
        return True

    def verify_key(self, raw_key: str) -> Optional[APIKey]:
        key_hash = _hash_key(raw_key)
        now = _utc_now().replace(tzinfo=None)
        row = (
            self.db.query(APIKey)
            .filter(APIKey.key_hash == key_hash, APIKey.is_active == True)
            .first()
        )
        if not row:
            return None
        if row.expires_at and row.expires_at.replace(tzinfo=None) <= now:
            return None
        row.last_used_at = _utc_now()
        self.db.commit()
        return row
