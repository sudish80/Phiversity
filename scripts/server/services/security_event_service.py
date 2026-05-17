"""Security event tracking and optional notification dispatch."""

import json
import os
from datetime import datetime, timezone
from typing import Optional

import requests
from sqlalchemy.orm import Session

from ..models import SecurityEvent


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SecurityEventService:
    def __init__(self, db: Session):
        self.db = db

    def create_event(
        self,
        event_type: str,
        severity: str,
        user_id: Optional[int] = None,
        source: Optional[str] = None,
        description: Optional[str] = None,
        client_ip: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SecurityEvent:
        row = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            source=source,
            description=description,
            client_ip=client_ip,
            event_metadata=json.dumps(metadata or {}),
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        self._maybe_notify(row)
        return row

    def _maybe_notify(self, event: SecurityEvent) -> None:
        webhook = os.getenv("SECURITY_ALERT_WEBHOOK_URL", "").strip()
        notify_severities = {"high", "critical"}
        if not webhook or event.severity not in notify_severities:
            return

        payload = {
            "event_id": event.id,
            "event_type": event.event_type,
            "severity": event.severity,
            "user_id": event.user_id,
            "source": event.source,
            "description": event.description,
            "client_ip": event.client_ip,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }

        try:
            requests.post(webhook, json=payload, timeout=5)
            event.notified_at = _utc_now()
            self.db.commit()
        except Exception:
            # Keep event regardless of notification failures.
            self.db.rollback()
