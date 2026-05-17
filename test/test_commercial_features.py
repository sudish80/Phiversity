import os
import hmac
import json
import hashlib
import unittest
from unittest.mock import patch

from test import _test_env  # noqa: F401

from fastapi.testclient import TestClient

from scripts.server.app import app
from scripts.server.auth import create_access_token, get_password_hash
from scripts.server.database import SessionLocal, engine
from scripts.server.models import (
    JobModel,
    PasswordResetToken,
    PaymentAccount,
    PaymentInvoice,
    PaymentTransaction,
    QualityTier,
    RefreshToken,
    RevokedAccessToken,
    Subscription,
    User,
    UserRole,
)


class CommercialFeaturesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        engine.dispose()

    def setUp(self):
        with SessionLocal() as db:
            db.query(PaymentTransaction).delete()
            db.query(PaymentInvoice).delete()
            db.query(Subscription).delete()
            db.query(PaymentAccount).delete()
            db.query(JobModel).delete()
            db.query(PasswordResetToken).delete()
            db.query(RefreshToken).delete()
            db.query(RevokedAccessToken).delete()
            db.query(User).delete()
            db.commit()

            admin = User(
                email="admin-biz@example.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.ADMIN,
            )
            member = User(
                email="member-biz@example.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.USER,
            )
            db.add_all([admin, member])
            db.commit()
            db.refresh(admin)
            db.refresh(member)

            self.admin_email = admin.email
            self.member_email = member.email
            self.member_id = member.id

    def _auth_headers(self, email: str) -> dict:
        token = create_access_token(data={"sub": email})
        return {"Authorization": f"Bearer {token}"}

    def _stripe_signed_payload_headers(self, payload: dict, *, timestamp: str = "1710000000") -> tuple[str, dict]:
        secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
        payload_json = json.dumps(payload, separators=(",", ":"))
        signed = f"{timestamp}.{payload_json}".encode("utf-8")
        signature = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
        return payload_json, {
            "Stripe-Signature": f"t={timestamp},v1={signature}",
            "Content-Type": "application/json",
        }

    def _paypal_signed_payload_headers(self, payload: dict) -> tuple[str, dict]:
        secret = os.environ.get("PAYPAL_WEBHOOK_SECRET", "")
        payload_json = json.dumps(payload, separators=(",", ":"))
        signature = hmac.new(secret.encode("utf-8"), payload_json.encode("utf-8"), hashlib.sha256).hexdigest()
        return payload_json, {
            "PayPal-Transmission-Sig": signature,
            "Content-Type": "application/json",
        }

    def test_social_start_returns_url_when_google_configured(self):
        with patch.dict(os.environ, {
            "GOOGLE_CLIENT_ID": "google-client-id-test",
            "GOOGLE_CLIENT_SECRET": "google-client-secret-test",
        }, clear=False):
            res = self.client.get(
                "/api/v1/auth/social/google/start",
                params={"redirect_uri": "http://localhost:8000/?social_provider=google"},
            )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["provider"], "google")
        self.assertTrue(data["authorization_url"].startswith("https://accounts.google.com/o/oauth2/v2/auth"))
        self.assertTrue(data["state"])

    def test_billing_tiers_requires_auth(self):
        res = self.client.get("/api/v1/billing/tiers")
        self.assertEqual(res.status_code, 401)

    def test_billing_checkout_returns_provider_url(self):
        res = self.client.post(
            "/api/v1/billing/checkout",
            headers=self._auth_headers(self.member_email),
            json={
                "provider": "stripe",
                "tier": "premium",
                "success_url": "http://localhost:8000/success",
                "cancel_url": "http://localhost:8000/cancel",
            },
        )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["provider"], "stripe")
        self.assertEqual(data["tier"], "premium")
        self.assertTrue(data["checkout_url"])
        self.assertTrue(data["session_ref"])

    def test_billing_tiers_include_metadata_catalog(self):
        res = self.client.get(
            "/api/v1/billing/tiers",
            headers=self._auth_headers(self.member_email),
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("tier_catalog", data)
        self.assertIn("recommended_tier", data)
        self.assertIn("currency", data)
        self.assertEqual(data["currency"], "USD")
        self.assertIn("premium", data["tier_catalog"])
        premium = data["tier_catalog"]["premium"]
        self.assertIn("display_name", premium)
        self.assertIn("badge", premium)
        self.assertIn("summary", premium)
        self.assertIn("features", premium)

    def test_admin_email_health_requires_admin(self):
        res = self.client.get(
            "/api/v1/admin/system/email-health",
            headers=self._auth_headers(self.member_email),
        )
        self.assertEqual(res.status_code, 403)

    def test_stripe_webhook_rejects_invalid_signature(self):
        payload = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {
                        "user_id": "1",
                        "tier": "premium",
                    }
                }
            }
        }
        res = self.client.post(
            "/api/v1/billing/webhooks/stripe",
            json=payload,
            headers={"Stripe-Signature": "t=1,v1=invalid"},
        )
        self.assertEqual(res.status_code, 401)

    def test_stripe_webhook_completed_syncs_user_tier(self):
        payload = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {
                        "user_id": str(self.member_id),
                        "tier": "premium",
                    }
                }
            }
        }

        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "test-stripe-secret"}, clear=False):
            payload_json, headers = self._stripe_signed_payload_headers(payload)
            res = self.client.post(
                "/api/v1/billing/webhooks/stripe",
                data=payload_json,
                headers=headers,
            )

        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body.get("sync_applied"))
        self.assertEqual(body.get("tier"), "premium")

        with SessionLocal() as db:
            user = db.query(User).filter(User.id == self.member_id).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.quality_tier.value, "premium")

    def test_stripe_webhook_subscription_deleted_downgrades_to_free(self):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == self.member_id).first()
            self.assertIsNotNone(user)
            user.quality_tier = QualityTier.PREMIUM
            db.commit()

        payload = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "metadata": {
                        "user_id": str(self.member_id)
                    }
                }
            }
        }

        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "test-stripe-secret"}, clear=False):
            payload_json, headers = self._stripe_signed_payload_headers(payload)
            res = self.client.post(
                "/api/v1/billing/webhooks/stripe",
                data=payload_json,
                headers=headers,
            )

        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body.get("sync_applied"))
        self.assertEqual(body.get("tier"), "free")

        with SessionLocal() as db:
            user = db.query(User).filter(User.id == self.member_id).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.quality_tier.value, "free")

    def test_stripe_webhook_persists_subscription_invoice_transaction_rows(self):
        payload = {
            "type": "invoice.paid",
            "data": {
                "object": {
                    "id": "in_test_123",
                    "invoice": "in_test_123",
                    "subscription": "sub_test_123",
                    "payment_intent": "pi_test_123",
                    "customer": "cus_test_123",
                    "customer_email": "member-biz@example.com",
                    "metadata": {
                        "user_id": str(self.member_id),
                        "tier": "premium",
                        "tenant_id": "tenant_a",
                    },
                    "status": "paid",
                    "currency": "usd",
                    "amount_due": 4900,
                    "amount_paid": 4900,
                    "created": 1710000000,
                    "status_transitions": {"paid_at": 1710000001},
                    "hosted_invoice_url": "https://billing.example/invoice/in_test_123",
                    "invoice_pdf": "https://billing.example/invoice/in_test_123.pdf",
                }
            },
        }

        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "test-stripe-secret"}, clear=False):
            payload_json, headers = self._stripe_signed_payload_headers(payload)
            res = self.client.post(
                "/api/v1/billing/webhooks/stripe",
                data=payload_json,
                headers=headers,
            )

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json().get("persistence_applied"))

        with SessionLocal() as db:
            account = db.query(PaymentAccount).filter(PaymentAccount.provider_customer_id == "cus_test_123").first()
            self.assertIsNotNone(account)
            self.assertEqual(account.user_id, self.member_id)

            subscription = db.query(Subscription).filter(Subscription.provider_subscription_id == "sub_test_123").first()
            self.assertIsNotNone(subscription)
            self.assertEqual(subscription.user_id, self.member_id)
            self.assertEqual(subscription.tier, "premium")

            invoice = db.query(PaymentInvoice).filter(PaymentInvoice.provider_invoice_id == "in_test_123").first()
            self.assertIsNotNone(invoice)
            self.assertEqual(invoice.subscription_id, subscription.id)
            self.assertEqual(invoice.amount_paid_cents, 4900)

            tx = db.query(PaymentTransaction).filter(PaymentTransaction.provider_payment_id == "pi_test_123").first()
            self.assertIsNotNone(tx)
            self.assertEqual(tx.subscription_id, subscription.id)
            self.assertEqual(tx.invoice_id, invoice.id)
            self.assertEqual(tx.status, "succeeded")

    def test_paypal_webhook_rejects_invalid_signature(self):
        payload = {
            "event_type": "BILLING.SUBSCRIPTION.ACTIVATED",
            "resource": {
                "custom_id": f"user_id={self.member_id};tier=premium"
            },
        }
        res = self.client.post(
            "/api/v1/billing/webhooks/paypal",
            json=payload,
            headers={"PayPal-Transmission-Sig": "invalid"},
        )
        self.assertEqual(res.status_code, 401)

    def test_paypal_webhook_activated_syncs_user_tier(self):
        payload = {
            "event_type": "BILLING.SUBSCRIPTION.ACTIVATED",
            "resource": {
                "custom_id": f"user_id={self.member_id};tier=premium"
            },
        }

        with patch.dict(os.environ, {"PAYPAL_WEBHOOK_SECRET": "test-paypal-secret"}, clear=False):
            payload_json, headers = self._paypal_signed_payload_headers(payload)
            res = self.client.post(
                "/api/v1/billing/webhooks/paypal",
                data=payload_json,
                headers=headers,
            )

        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body.get("sync_applied"))
        self.assertEqual(body.get("tier"), "premium")

        with SessionLocal() as db:
            user = db.query(User).filter(User.id == self.member_id).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.quality_tier.value, "premium")

    def test_paypal_webhook_subscription_cancelled_downgrades_to_free(self):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == self.member_id).first()
            self.assertIsNotNone(user)
            user.quality_tier = QualityTier.PREMIUM
            db.commit()

        payload = {
            "event_type": "BILLING.SUBSCRIPTION.CANCELLED",
            "resource": {
                "custom_id": f"user_id={self.member_id}"
            },
        }

        with patch.dict(os.environ, {"PAYPAL_WEBHOOK_SECRET": "test-paypal-secret"}, clear=False):
            payload_json, headers = self._paypal_signed_payload_headers(payload)
            res = self.client.post(
                "/api/v1/billing/webhooks/paypal",
                data=payload_json,
                headers=headers,
            )

        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body.get("sync_applied"))
        self.assertEqual(body.get("tier"), "free")

        with SessionLocal() as db:
            user = db.query(User).filter(User.id == self.member_id).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.quality_tier.value, "free")

    def test_paypal_webhook_subscription_suspended_downgrades_to_free(self):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == self.member_id).first()
            self.assertIsNotNone(user)
            user.quality_tier = QualityTier.PREMIUM
            db.commit()

        payload = {
            "event_type": "BILLING.SUBSCRIPTION.SUSPENDED",
            "resource": {
                "custom_id": f"user_id={self.member_id}"
            },
        }

        with patch.dict(os.environ, {"PAYPAL_WEBHOOK_SECRET": "test-paypal-secret"}, clear=False):
            payload_json, headers = self._paypal_signed_payload_headers(payload)
            res = self.client.post(
                "/api/v1/billing/webhooks/paypal",
                data=payload_json,
                headers=headers,
            )

        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body.get("sync_applied"))
        self.assertEqual(body.get("tier"), "free")

        with SessionLocal() as db:
            user = db.query(User).filter(User.id == self.member_id).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.quality_tier.value, "free")

    def test_paypal_webhook_persists_subscription_invoice_transaction_rows(self):
        payload = {
            "event_type": "PAYMENT.SALE.COMPLETED",
            "resource": {
                "id": "sale_test_123",
                "state": "completed",
                "create_time": "2026-03-25T10:00:00Z",
                "billing_agreement_id": "I-SUB-TEST-123",
                "invoice_number": "INV-PP-123",
                "custom_id": f"user_id={self.member_id};tier=premium;tenant_id=tenant_b",
                "amount": {"total": "49.00", "currency": "USD"},
                "payer": {
                    "payer_id": "payer_test_123",
                    "email_address": "member-biz@example.com",
                },
            },
        }

        with patch.dict(os.environ, {"PAYPAL_WEBHOOK_SECRET": "test-paypal-secret"}, clear=False):
            payload_json, headers = self._paypal_signed_payload_headers(payload)
            res = self.client.post(
                "/api/v1/billing/webhooks/paypal",
                data=payload_json,
                headers=headers,
            )

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json().get("persistence_applied"))

        with SessionLocal() as db:
            account = db.query(PaymentAccount).filter(PaymentAccount.provider_customer_id == "payer_test_123").first()
            self.assertIsNotNone(account)
            self.assertEqual(account.user_id, self.member_id)

            subscription = db.query(Subscription).filter(Subscription.provider_subscription_id == "I-SUB-TEST-123").first()
            self.assertIsNotNone(subscription)
            self.assertEqual(subscription.tier, "premium")

            invoice = db.query(PaymentInvoice).filter(PaymentInvoice.provider_invoice_id == "INV-PP-123").first()
            self.assertIsNotNone(invoice)
            self.assertEqual(invoice.subscription_id, subscription.id)

            tx = db.query(PaymentTransaction).filter(PaymentTransaction.provider_payment_id == "sale_test_123").first()
            self.assertIsNotNone(tx)
            self.assertEqual(tx.amount_cents, 4900)
            self.assertEqual(tx.status, "succeeded")


if __name__ == "__main__":
    unittest.main()
