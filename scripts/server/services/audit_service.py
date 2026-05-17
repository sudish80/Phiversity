"""
Audit logging service for security-relevant events.
Logs all authentication, authorization, and sensitive operations.
"""
import json
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from ..models import AuditLog


class AuditService:
    """Service for logging security-relevant events to audit trail."""

    @staticmethod
    def log_event(
        db: Session,
        event_type: str,
        status: str,
        user_id: Optional[int] = None,
        description: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_path: Optional[str] = None,
        request_method: Optional[str] = None,
        response_status: Optional[int] = None,
        error_message: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AuditLog:
        """
        Log a security-relevant event.

        Args:
            db: Database session
            event_type: Type of event (login, logout, password_reset, token_refresh, signup, etc.)
            status: Event status (success, failure)
            user_id: ID of user involved (optional for signup/forgot-password)
            description: Human-readable description
            client_ip: Client IP address
            user_agent: Client user agent
            request_path: API endpoint path
            request_method: HTTP method
            response_status: HTTP response status code
            error_message: Error message if failed
            metadata: Additional context as dict (will be JSON serialized)

        Returns:
            Created AuditLog record
        """
        metadata_json = None
        if metadata:
            metadata_json = json.dumps(metadata)

        audit_log = AuditLog(
            user_id=user_id,
            event_type=event_type,
            status=status,
            description=description,
            client_ip=client_ip,
            user_agent=user_agent,
            request_path=request_path,
            request_method=request_method,
            response_status=response_status,
            error_message=error_message,
            audit_metadata=metadata_json,
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log

    @staticmethod
    def get_user_audit_trail(
        db: Session,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
        event_types: Optional[list[str]] = None,
    ) -> list[AuditLog]:
        """
        Retrieve audit logs for a specific user.

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of records to return
            offset: Offset for pagination
            event_types: Filter by specific event types (optional)

        Returns:
            List of AuditLog records
        """
        query = db.query(AuditLog).filter(AuditLog.user_id == user_id)

        if event_types:
            query = query.filter(AuditLog.event_type.in_(event_types))

        return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_audit_logs(
        db: Session,
        limit: int = 100,
        offset: int = 0,
        event_types: Optional[list[str]] = None,
        status: Optional[str] = None,
    ) -> list[AuditLog]:
        """
        Retrieve system audit logs (admin view).

        Args:
            db: Database session
            limit: Maximum number of records to return
            offset: Offset for pagination
            event_types: Filter by specific event types (optional)
            status: Filter by status (success/failure, optional)

        Returns:
            List of AuditLog records
        """
        query = db.query(AuditLog)

        if event_types:
            query = query.filter(AuditLog.event_type.in_(event_types))

        if status:
            query = query.filter(AuditLog.status == status)

        return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def cleanup_old_audit_logs(
        db: Session,
        retention_days: int = 90,
    ) -> int:
        """
        Delete audit logs older than retention period.

        Args:
            db: Database session
            retention_days: Number of days to retain logs

        Returns:
            Number of deleted records
        """
        from datetime import timedelta

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        result = db.query(AuditLog).filter(AuditLog.created_at < cutoff_date).delete()
        db.commit()
        return result
