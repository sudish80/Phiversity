"""OAuth2 provider scaffolding helpers (client and authorization-code management)."""

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from ..models import OAuthAuthorizationCode, OAuthClient


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class OAuthScaffoldService:
    def __init__(self, db: Session):
        self.db = db

    def create_client(self, name: str, redirect_uris: list[str], scopes: list[str], grants: list[str]) -> tuple[OAuthClient, str]:
        client_id = f"cli_{secrets.token_urlsafe(18)}"
        raw_secret = secrets.token_urlsafe(36)
        row = OAuthClient(
            name=name,
            client_id=client_id,
            client_secret_hash=hash_secret(raw_secret),
            redirect_uris=json.dumps(redirect_uris),
            scopes=json.dumps(scopes),
            grants=json.dumps(grants),
            is_active=True,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row, raw_secret

    def verify_client(self, client_id: str, client_secret: str) -> Optional[OAuthClient]:
        row = self.db.query(OAuthClient).filter(OAuthClient.client_id == client_id, OAuthClient.is_active == True).first()
        if not row:
            return None
        if row.client_secret_hash != hash_secret(client_secret):
            return None
        return row

    def create_authorization_code(
        self,
        client_id: str,
        user_id: int,
        redirect_uri: str,
        scope: str,
        ttl_minutes: int = 10,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
    ) -> str:
        raw_code = secrets.token_urlsafe(32)
        row = OAuthAuthorizationCode(
            client_id=client_id,
            user_id=user_id,
            code_hash=hash_secret(raw_code),
            redirect_uri=redirect_uri,
            scope=scope,
            expires_at=_utc_now() + timedelta(minutes=ttl_minutes),
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
        self.db.add(row)
        self.db.commit()
        return raw_code

    def consume_authorization_code(self, raw_code: str, client_id: str, redirect_uri: str) -> Optional[OAuthAuthorizationCode]:
        now = _utc_now().replace(tzinfo=None)
        row = (
            self.db.query(OAuthAuthorizationCode)
            .filter(
                OAuthAuthorizationCode.code_hash == hash_secret(raw_code),
                OAuthAuthorizationCode.client_id == client_id,
                OAuthAuthorizationCode.redirect_uri == redirect_uri,
            )
            .first()
        )
        if not row:
            return None
        if row.used_at is not None:
            return None
        expires_at = row.expires_at.replace(tzinfo=None) if row.expires_at.tzinfo else row.expires_at
        if expires_at <= now:
            return None

        row.used_at = _utc_now()
        self.db.commit()
        return row
