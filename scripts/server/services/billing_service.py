"""Billing helpers for Stripe/PayPal checkout and webhook payload normalization."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from typing import Any
from urllib.parse import urlencode


DEFAULT_TIERS = {
    "free": {
        "amount_usd": 0,
        "yearly_amount_usd": 0,
        "display_name": "Free",
        "badge": "Starter",
        "summary": "Get started with watermark-enabled exports.",
        "features": ["Watermarked videos", "Basic queue priority"],
    },
    "standard": {
        "amount_usd": 19,
        "yearly_amount_usd": 190,
        "display_name": "Standard",
        "badge": "Most Flexible",
        "summary": "Balanced quality and speed for solo creators.",
        "features": ["720p exports", "Priority queue"],
    },
    "premium": {
        "amount_usd": 49,
        "yearly_amount_usd": 490,
        "display_name": "Premium",
        "badge": "Best Value",
        "recommended": True,
        "summary": "Fast workflow with 1080p and no watermark.",
        "features": ["1080p exports", "Fast queue", "No watermark"],
    },
    "enterprise": {
        "amount_usd": 199,
        "yearly_amount_usd": 1990,
        "display_name": "Enterprise",
        "badge": "Scale",
        "summary": "Advanced controls and support for teams.",
        "features": ["Custom branding", "SSO/SAML", "Dedicated support"],
    },
}


class BillingService:
    def __init__(self) -> None:
        self.stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY", "").strip()
        self.stripe_checkout_base = os.getenv("STRIPE_CHECKOUT_BASE_URL", "https://checkout.stripe.com/pay")
        self.paypal_checkout_base = os.getenv("PAYPAL_CHECKOUT_BASE_URL", "https://www.paypal.com/checkoutnow")
        self.portal_base = os.getenv("BILLING_PORTAL_URL", "")

    def get_tiers(self) -> dict[str, Any]:
        raw = os.getenv("SUBSCRIPTION_TIERS_JSON", "").strip()
        if not raw:
            return DEFAULT_TIERS
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and parsed:
                return parsed
        except Exception:
            pass
        return DEFAULT_TIERS

    def create_checkout(self, provider: str, tier: str, user_id: int, tenant_id: str | None, success_url: str, cancel_url: str) -> dict[str, Any]:
        normalized_provider = provider.strip().lower()
        session_ref = secrets.token_urlsafe(18)
        query = {
            "session_ref": session_ref,
            "tier": tier,
            "user_id": str(user_id),
            "tenant_id": tenant_id or "default",
            "success_url": success_url,
            "cancel_url": cancel_url,
        }

        if normalized_provider == "stripe":
            checkout_url = f"{self.stripe_checkout_base}?{urlencode(query)}"
        elif normalized_provider == "paypal":
            checkout_url = f"{self.paypal_checkout_base}?{urlencode(query)}"
        else:
            raise ValueError("Unsupported provider")

        return {
            "provider": normalized_provider,
            "checkout_url": checkout_url,
            "session_ref": session_ref,
        }

    def portal_url(self, user_id: int, tenant_id: str | None) -> str | None:
        if not self.portal_base:
            return None
        return f"{self.portal_base}?{urlencode({'user_id': str(user_id), 'tenant_id': tenant_id or 'default'})}"

    def verify_stripe_signature(self, payload: bytes, signature_header: str | None) -> bool:
        secret = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()
        if not secret:
            return False
        if not signature_header:
            return False

        parts = {}
        for piece in signature_header.split(','):
            if '=' in piece:
                k, v = piece.split('=', 1)
                parts[k.strip()] = v.strip()
        timestamp = parts.get('t')
        sent_sig = parts.get('v1')
        if not timestamp or not sent_sig:
            return False

        signed_payload = f"{timestamp}.{payload.decode('utf-8', errors='ignore')}".encode('utf-8')
        computed = hmac.new(secret.encode('utf-8'), signed_payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, sent_sig)

    def verify_paypal_signature(self, transmission_sig: str | None, payload: bytes) -> bool:
        secret = os.getenv("PAYPAL_WEBHOOK_SECRET", "").strip()
        if not secret or not transmission_sig:
            return False
        computed = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, transmission_sig)
