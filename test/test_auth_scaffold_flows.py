import os
import unittest
import hashlib
import base64
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, parse_qs

from test import _test_env  # noqa: F401  Ensures test DB env vars are set before app import.

from fastapi.testclient import TestClient

import scripts.server.app as app_module
from scripts.server.app import app
from scripts.server.auth import get_password_hash
from scripts.server.database import SessionLocal, engine
from scripts.server.models import (
    JobModel,
    PasswordResetToken,
    RefreshToken,
    RevokedAccessToken,
    AuditLog,
    LoginAttempt,
    EmailVerificationToken,
    APIKey,
    SecurityEvent,
    PasswordlessLoginToken,
    OAuthClient,
    OAuthAuthorizationCode,
    WebAuthnCredential,
    SAMLIdentityProvider,
    User,
    UserRole,
)


def _pkce_s256_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


class AuthScaffoldFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        engine.dispose()

    def setUp(self):
        self._old_debug_passwordless = os.getenv("AUTH_DEBUG_EXPOSE_PASSWORDLESS_TOKEN")
        self._old_saml_hint = os.getenv("SAML_SCAFFOLD_ACCEPT_EMAIL_HINT")

        os.environ["AUTH_DEBUG_EXPOSE_PASSWORDLESS_TOKEN"] = "true"
        os.environ["SAML_SCAFFOLD_ACCEPT_EMAIL_HINT"] = "true"
        app_module._WEBAUTHN_CHALLENGES.clear()
        app_module._SOCIAL_AUTH_STATES.clear()

        with SessionLocal() as db:
            # Clear in child-first order for FK safety.
            db.query(OAuthAuthorizationCode).delete()
            db.query(OAuthClient).delete()
            db.query(WebAuthnCredential).delete()
            db.query(SAMLIdentityProvider).delete()
            db.query(PasswordlessLoginToken).delete()
            db.query(EmailVerificationToken).delete()
            db.query(LoginAttempt).delete()
            db.query(AuditLog).delete()
            db.query(APIKey).delete()
            db.query(SecurityEvent).delete()
            db.query(PasswordResetToken).delete()
            db.query(RefreshToken).delete()
            db.query(RevokedAccessToken).delete()
            db.query(JobModel).delete()
            db.query(User).delete()
            db.commit()

            user = User(
                email="scaffold-user@example.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.USER,
            )
            admin = User(
                email="scaffold-admin@example.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.ADMIN,
            )
            db.add(user)
            db.add(admin)
            db.commit()

        self.user_email = "scaffold-user@example.com"
        self.admin_email = "scaffold-admin@example.com"
        self.password = "password123"

    def tearDown(self):
        if self._old_debug_passwordless is None:
            os.environ.pop("AUTH_DEBUG_EXPOSE_PASSWORDLESS_TOKEN", None)
        else:
            os.environ["AUTH_DEBUG_EXPOSE_PASSWORDLESS_TOKEN"] = self._old_debug_passwordless

        if self._old_saml_hint is None:
            os.environ.pop("SAML_SCAFFOLD_ACCEPT_EMAIL_HINT", None)
        else:
            os.environ["SAML_SCAFFOLD_ACCEPT_EMAIL_HINT"] = self._old_saml_hint

    def _login(self, email: str, password: str) -> dict:
        res = self.client.post("/api/v1/auth/token", json={"email": email, "password": password})
        self.assertEqual(res.status_code, 200, res.text)
        return res.json()

    def test_passwordless_request_and_verify(self):
        req_res = self.client.post(
            "/api/v1/auth/passwordless/request",
            json={"email": self.user_email},
        )
        self.assertEqual(req_res.status_code, 200, req_res.text)

        body = req_res.json()
        self.assertIn("debug_token", body)
        self.assertTrue(body["debug_token"])

        verify_res = self.client.post(
            "/api/v1/auth/passwordless/verify",
            json={"token": body["debug_token"]},
        )
        self.assertEqual(verify_res.status_code, 200, verify_res.text)

        token_payload = verify_res.json()
        self.assertIn("access_token", token_payload)
        self.assertIn("refresh_token", token_payload)

    def test_oauth_authorization_code_flow_with_pkce(self):
        admin_tokens = self._login(self.admin_email, self.password)
        admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}

        client_res = self.client.post(
            "/api/v1/admin/oauth/clients",
            headers=admin_headers,
            json={
                "name": "Integration Test Client",
                "redirect_uris": ["https://client.example/callback"],
                "scopes": ["read_jobs", "user:read"],
                "grants": ["authorization_code", "client_credentials"],
            },
        )
        self.assertEqual(client_res.status_code, 200, client_res.text)
        client_data = client_res.json()

        user_tokens = self._login(self.user_email, self.password)
        user_headers = {"Authorization": f"Bearer {user_tokens['access_token']}"}

        code_verifier = "verifier-value-1234567890"
        code_challenge = _pkce_s256_challenge(code_verifier)

        auth_res = self.client.get(
            "/api/v1/oauth/authorize",
            headers=user_headers,
            params={
                "response_type": "code",
                "client_id": client_data["client_id"],
                "redirect_uri": "https://client.example/callback",
                "scope": "read_jobs user:read",
                "state": "xyz-state",
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            },
        )
        self.assertEqual(auth_res.status_code, 200, auth_res.text)
        redirect_to = auth_res.json()["redirect_to"]

        parsed = urlparse(redirect_to)
        query = parse_qs(parsed.query)
        self.assertIn("code", query)
        code = query["code"][0]

        token_res = self.client.post(
            "/api/v1/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": client_data["client_id"],
                "client_secret": client_data["client_secret"],
                "code": code,
                "redirect_uri": "https://client.example/callback",
                "code_verifier": code_verifier,
            },
        )
        self.assertEqual(token_res.status_code, 200, token_res.text)
        token_body = token_res.json()
        self.assertIn("access_token", token_body)
        self.assertEqual(token_body["token_type"], "bearer")

    def test_webauthn_stub_register_and_authenticate(self):
        user_tokens = self._login(self.user_email, self.password)
        headers = {"Authorization": f"Bearer {user_tokens['access_token']}"}

        options_res = self.client.post("/api/v1/auth/webauthn/register/options", headers=headers)
        self.assertEqual(options_res.status_code, 200, options_res.text)
        register_challenge = options_res.json()["challenge"]

        verify_reg_res = self.client.post(
            "/api/v1/auth/webauthn/register/verify",
            headers=headers,
            json={
                "challenge": register_challenge,
                "credential_id": "cred-test-001",
                "public_key": "public-key-test-value",
                "sign_count": 0,
                "aaguid": "test-aaguid",
                "transports": ["internal"],
            },
        )
        self.assertEqual(verify_reg_res.status_code, 200, verify_reg_res.text)

        auth_options_res = self.client.post(
            "/api/v1/auth/webauthn/authenticate/options",
            json={"email": self.user_email},
        )
        self.assertEqual(auth_options_res.status_code, 200, auth_options_res.text)
        auth_payload = auth_options_res.json()
        auth_challenge = auth_payload["challenge"]
        self.assertTrue(len(auth_payload["allow_credentials"]) >= 1)

        verify_auth_res = self.client.post(
            "/api/v1/auth/webauthn/authenticate/verify",
            json={
                "email": self.user_email,
                "credential_id": "cred-test-001",
                "challenge": auth_challenge,
            },
        )
        self.assertEqual(verify_auth_res.status_code, 200, verify_auth_res.text)
        token_body = verify_auth_res.json()
        self.assertIn("access_token", token_body)
        self.assertIn("refresh_token", token_body)

    def test_saml_stub_provider_metadata_login_and_acs(self):
        admin_tokens = self._login(self.admin_email, self.password)
        admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}

        provider_res = self.client.post(
            "/api/v1/admin/saml/providers",
            headers=admin_headers,
            json={
                "name": "Test IdP",
                "entity_id": "urn:test:idp",
                "sso_url": "https://idp.example/sso",
                "x509_cert": "-----BEGIN CERTIFICATE-----TEST-----END CERTIFICATE-----",
                "acs_url": "https://sp.example/acs",
            },
        )
        self.assertEqual(provider_res.status_code, 200, provider_res.text)
        provider_id = provider_res.json()["provider_id"]

        metadata_res = self.client.get("/api/v1/auth/saml/metadata")
        self.assertEqual(metadata_res.status_code, 200, metadata_res.text)
        self.assertIn("EntityDescriptor", metadata_res.text)

        login_res = self.client.get(
            "/api/v1/auth/saml/login",
            params={"provider_id": provider_id, "relay_state": "state-abc"},
        )
        self.assertEqual(login_res.status_code, 200, login_res.text)
        self.assertIn("redirect_to", login_res.json())

        acs_res = self.client.post(
            "/api/v1/auth/saml/acs",
            json={
                "saml_response": "stub-saml-response",
                "relay_state": "state-abc",
                "email_hint": self.user_email,
            },
        )
        self.assertEqual(acs_res.status_code, 200, acs_res.text)
        acs_body = acs_res.json()
        self.assertIn("access_token", acs_body)
        self.assertIn("refresh_token", acs_body)

    def test_webauthn_challenge_map_is_pruned_when_over_limit(self):
        original_limit = app_module._WEBAUTHN_CHALLENGE_MAX_ENTRIES
        try:
            app_module._WEBAUTHN_CHALLENGE_MAX_ENTRIES = 3
            now = datetime.now(timezone.utc)
            app_module._WEBAUTHN_CHALLENGES.clear()
            app_module._WEBAUTHN_CHALLENGES["expired"] = now - timedelta(seconds=1)
            app_module._WEBAUTHN_CHALLENGES["k1"] = now + timedelta(seconds=60)
            app_module._WEBAUTHN_CHALLENGES["k2"] = now + timedelta(seconds=60)
            app_module._WEBAUTHN_CHALLENGES["k3"] = now + timedelta(seconds=60)
            app_module._WEBAUTHN_CHALLENGES["k4"] = now + timedelta(seconds=60)

            app_module._prune_webauthn_challenges()

            self.assertNotIn("expired", app_module._WEBAUTHN_CHALLENGES)
            self.assertLessEqual(len(app_module._WEBAUTHN_CHALLENGES), 3)
            self.assertNotIn("k1", app_module._WEBAUTHN_CHALLENGES)
        finally:
            app_module._WEBAUTHN_CHALLENGE_MAX_ENTRIES = original_limit


if __name__ == "__main__":
    unittest.main()
