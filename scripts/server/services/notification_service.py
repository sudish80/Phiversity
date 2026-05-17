"""Transactional email delivery helpers for verification, password reset, and billing notices."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class EmailSendResult:
    sent: bool
    provider: str
    status_code: int | None = None
    detail: str | None = None


class NotificationService:
    def __init__(self) -> None:
        self.provider = (os.getenv("EMAIL_PROVIDER", "log").strip().lower() or "log")
        self.from_email = os.getenv("EMAIL_FROM", "no-reply@phiversity.local").strip()
        self.base_url = (os.getenv("PUBLIC_BASE_URL", "").strip() or "http://localhost:8000").rstrip("/")

    def send_password_reset_email(self, email: str, raw_token: str) -> EmailSendResult:
        reset_url = f"{self.base_url}/?reset_token={raw_token}"
        subject = "Reset your Phiversity password"
        body = (
            "We received a request to reset your password. "
            f"Use this link to continue: {reset_url}\n\n"
            "If you did not request this, you can ignore this email."
        )
        return self.send_email(email, subject, body)

    def send_verification_email(self, email: str, raw_token: str) -> EmailSendResult:
        verify_url = f"{self.base_url}/?verify_token={raw_token}"
        subject = "Verify your Phiversity email"
        body = (
            "Welcome to Phiversity. "
            f"Please verify your account: {verify_url}\n\n"
            "If you did not create this account, ignore this email."
        )
        return self.send_email(email, subject, body)

    def send_payment_confirmation_email(self, email: str, tier: str, provider: str) -> EmailSendResult:
        subject = "Your Phiversity subscription has been updated"
        body = (
            f"Your subscription is now active on tier '{tier}' via {provider}.\n"
            "You can manage billing and invoices from your account dashboard."
        )
        return self.send_email(email, subject, body)

    def send_email(self, to_email: str, subject: str, body: str) -> EmailSendResult:
        if self.provider == "sendgrid":
            return self._send_via_sendgrid(to_email, subject, body)
        if self.provider == "mailgun":
            return self._send_via_mailgun(to_email, subject, body)
        if self.provider == "ses":
            return self._send_via_ses(to_email, subject, body)

        # Default safe mode for development: log-only
        print(
            json.dumps(
                {
                    "event": "email.log_only",
                    "provider": self.provider,
                    "to": to_email,
                    "subject": subject,
                }
            )
        )
        return EmailSendResult(sent=False, provider=self.provider, detail="log-only mode")

    def _send_via_sendgrid(self, to_email: str, subject: str, body: str) -> EmailSendResult:
        api_key = os.getenv("SENDGRID_API_KEY", "").strip()
        if not api_key:
            return EmailSendResult(sent=False, provider="sendgrid", detail="SENDGRID_API_KEY missing")

        payload: dict[str, Any] = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": self.from_email},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}],
        }
        resp = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=10,
        )
        ok = 200 <= resp.status_code < 300
        return EmailSendResult(
            sent=ok,
            provider="sendgrid",
            status_code=resp.status_code,
            detail=None if ok else (resp.text[:400] if resp.text else "sendgrid error"),
        )

    def _send_via_mailgun(self, to_email: str, subject: str, body: str) -> EmailSendResult:
        api_key = os.getenv("MAILGUN_API_KEY", "").strip()
        domain = os.getenv("MAILGUN_DOMAIN", "").strip()
        if not api_key or not domain:
            return EmailSendResult(sent=False, provider="mailgun", detail="MAILGUN_API_KEY/MAILGUN_DOMAIN missing")

        resp = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "text": body,
            },
            timeout=10,
        )
        ok = 200 <= resp.status_code < 300
        return EmailSendResult(
            sent=ok,
            provider="mailgun",
            status_code=resp.status_code,
            detail=None if ok else (resp.text[:400] if resp.text else "mailgun error"),
        )

    def _send_via_ses(self, to_email: str, subject: str, body: str) -> EmailSendResult:
        try:
            import boto3  # type: ignore
        except Exception:
            return EmailSendResult(sent=False, provider="ses", detail="boto3 unavailable")

        region = os.getenv("AWS_REGION", "us-east-1")
        ses_client = boto3.client("ses", region_name=region)
        try:
            ses_client.send_email(
                Source=self.from_email,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body}},
                },
            )
            return EmailSendResult(sent=True, provider="ses")
        except Exception as exc:
            return EmailSendResult(sent=False, provider="ses", detail=str(exc))
