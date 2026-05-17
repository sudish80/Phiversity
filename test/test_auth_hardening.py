import unittest
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from test import _test_env  # Ensures test DB env vars are configured before app import.

from fastapi.testclient import TestClient

from scripts.server.app import app
from scripts.server.auth import get_password_hash
from scripts.server.database import SessionLocal, engine
from scripts.server.models import AuthIdentity, JobModel, PasswordResetToken, RefreshToken, RevokedAccessToken, User, UserProfile, UserRole
import scripts.server.app as app_module
from scripts.server.services.user_service import UserService


class AuthHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        engine.dispose()

    def setUp(self):
        with SessionLocal() as db:
            db.query(UserProfile).delete()
            db.query(AuthIdentity).delete()
            db.query(JobModel).delete()
            db.query(PasswordResetToken).delete()
            db.query(RefreshToken).delete()
            db.query(RevokedAccessToken).delete()
            db.query(User).delete()
            db.commit()
            user = User(
                email="hardening@example.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.USER,
            )
            db.add(user)
            db.commit()

        self.email = "hardening@example.com"
        self.password = "password123"

    def _login(self):
        res = self.client.post(
            "/api/v1/auth/token",
            json={"email": self.email, "password": self.password},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        data["csrf_token"] = res.headers.get("X-CSRF-Token")
        return data

    def test_refresh_rotation_invalidates_old_refresh_token(self):
        login_data = self._login()

        refresh_res = self.client.post(
            "/api/v1/auth/refresh",
            headers={"X-CSRF-Token": login_data["csrf_token"]},
            json={"refresh_token": login_data["refresh_token"]},
        )
        self.assertEqual(refresh_res.status_code, 200)
        rotated = refresh_res.json()
        self.assertIn("access_token", rotated)
        self.assertIn("refresh_token", rotated)
        self.assertNotEqual(rotated["refresh_token"], login_data["refresh_token"])

        replay_res = self.client.post(
            "/api/v1/auth/refresh",
            headers={"X-CSRF-Token": refresh_res.headers.get("X-CSRF-Token")},
            json={"refresh_token": login_data["refresh_token"]},
        )
        self.assertEqual(replay_res.status_code, 401)

    def test_logout_revokes_access_and_refresh_tokens(self):
        login_data = self._login()
        headers = {"Authorization": f"Bearer {login_data['access_token']}"}

        me_before = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(me_before.status_code, 200)

        logout_res = self.client.post(
            "/api/v1/auth/logout",
            headers=headers,
            json={"refresh_token": login_data["refresh_token"]},
        )
        self.assertEqual(logout_res.status_code, 200)

        me_after = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(me_after.status_code, 401)

        refresh_after = self.client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": login_data["refresh_token"]},
        )
        self.assertEqual(refresh_after.status_code, 401)

    def test_reset_password_consumes_token_and_revokes_sessions(self):
        login_data = self._login()

        with SessionLocal() as db:
            service = UserService(db)
            user = service.get_user_by_email(self.email)
            reset_token = service.create_password_reset_token(user)

        reset_res = self.client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "N3w$Passw0rd!X",
            },
        )
        self.assertEqual(reset_res.status_code, 200)

        old_login = self.client.post(
            "/api/v1/auth/token",
            json={"email": self.email, "password": self.password},
        )
        self.assertEqual(old_login.status_code, 401)

        new_login = self.client.post(
            "/api/v1/auth/token",
            json={"email": self.email, "password": "N3w$Passw0rd!X"},
        )
        self.assertEqual(new_login.status_code, 200)

        refresh_after_reset = self.client.post(
            "/api/v1/auth/refresh",
            headers={"X-CSRF-Token": new_login.headers.get("X-CSRF-Token")},
            json={"refresh_token": login_data["refresh_token"]},
        )
        self.assertEqual(refresh_after_reset.status_code, 401)

    def test_cleanup_removes_expired_auth_records(self):
        now = datetime.now(timezone.utc)

        with SessionLocal() as db:
            service = UserService(db)
            user = service.get_user_by_email(self.email)

            expired_reset = PasswordResetToken(
                user_id=user.id,
                token_hash="expired-reset-token-hash",
                expires_at=now - timedelta(hours=1),
            )
            used_reset = PasswordResetToken(
                user_id=user.id,
                token_hash="used-reset-token-hash",
                expires_at=now + timedelta(hours=1),
                used_at=now - timedelta(minutes=5),
            )
            valid_reset = PasswordResetToken(
                user_id=user.id,
                token_hash="valid-reset-token-hash",
                expires_at=now + timedelta(hours=1),
            )

            expired_refresh = RefreshToken(
                user_id=user.id,
                token_hash="expired-refresh-token-hash",
                family_id="fam-expired",
                expires_at=now - timedelta(hours=1),
            )
            old_revoked_refresh = RefreshToken(
                user_id=user.id,
                token_hash="old-revoked-refresh-token-hash",
                family_id="fam-revoked",
                expires_at=now + timedelta(days=1),
                revoked_at=now - timedelta(days=2),
                revoked_reason="test",
            )
            valid_refresh = RefreshToken(
                user_id=user.id,
                token_hash="valid-refresh-token-hash",
                family_id="fam-valid",
                expires_at=now + timedelta(days=1),
            )

            expired_revoked_access = RevokedAccessToken(
                jti="expired-jti",
                user_id=user.id,
                expires_at=now - timedelta(minutes=1),
                reason="test",
            )
            valid_revoked_access = RevokedAccessToken(
                jti="valid-jti",
                user_id=user.id,
                expires_at=now + timedelta(days=1),
                reason="test",
            )

            db.add_all([
                expired_reset,
                used_reset,
                valid_reset,
                expired_refresh,
                old_revoked_refresh,
                valid_refresh,
                expired_revoked_access,
                valid_revoked_access,
            ])
            db.commit()

            deleted = service.cleanup_expired_auth_records(revoked_retention_seconds=3600)
            self.assertGreaterEqual(deleted["password_reset_tokens"], 2)
            self.assertGreaterEqual(deleted["refresh_tokens"], 2)
            self.assertGreaterEqual(deleted["revoked_access_tokens"], 1)

            self.assertIsNotNone(db.query(PasswordResetToken).filter_by(token_hash="valid-reset-token-hash").first())
            self.assertIsNotNone(db.query(RefreshToken).filter_by(token_hash="valid-refresh-token-hash").first())
            self.assertIsNotNone(db.query(RevokedAccessToken).filter_by(jti="valid-jti").first())

    def test_email_uniqueness_is_case_insensitive(self):
        dup_signup = self.client.post(
            "/api/v1/auth/signup",
            json={"email": "HARDENING@EXAMPLE.COM", "password": "another-pass-789"},
        )
        self.assertEqual(dup_signup.status_code, 400)

    def test_admin_login_alias_maps_to_admin_email(self):
        with SessionLocal() as db:
            admin_user = User(
                email="admin@phiversity.local",
                hashed_password=get_password_hash("PhiversityAdmin@123"),
                role=UserRole.ADMIN,
            )
            db.add(admin_user)
            db.commit()

        with patch.dict(os.environ, {"ADMIN_LOGIN_ID": "admin", "ADMIN_EMAIL": "admin@phiversity.local"}, clear=False):
            res = self.client.post(
                "/api/v1/auth/token",
                json={"email": "admin", "password": "PhiversityAdmin@123"},
            )

        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertIn("access_token", payload)

        mixed_case_login = self.client.post(
            "/api/v1/auth/token",
            json={"email": "HARDENING@EXAMPLE.COM", "password": self.password},
        )
        self.assertEqual(mixed_case_login.status_code, 200)

    def test_bootstrap_admin_creates_local_auth_identity(self):
        with SessionLocal() as db:
            db.query(AuthIdentity).delete()
            db.query(User).delete()
            db.commit()

        with patch.dict(
            os.environ,
            {
                "AUTO_CREATE_ADMIN": "true",
                "ADMIN_EMAIL": "admin@phiversity.local",
                "ADMIN_PASSWORD": "PhiversityAdmin@123",
                "PHIVERSITY_ENV": "development",
            },
            clear=False,
        ):
            app_module._ensure_bootstrap_admin_user()

        with SessionLocal() as db:
            admin = db.query(User).filter(User.email == "admin@phiversity.local").first()
            self.assertIsNotNone(admin)
            self.assertEqual(admin.role, UserRole.ADMIN)

            identity = (
                db.query(AuthIdentity)
                .filter(
                    AuthIdentity.user_id == admin.id,
                    AuthIdentity.provider == "local",
                )
                .first()
            )
            self.assertIsNotNone(identity)
            self.assertEqual(identity.provider_user_id, "admin@phiversity.local")
            self.assertEqual(identity.provider_email, "admin@phiversity.local")
            self.assertTrue(identity.is_primary)
            self.assertTrue(identity.is_verified)

    def test_password_hash_metadata_is_persisted_for_new_users(self):
        with SessionLocal() as db:
            service = UserService(db)
            created = service.create_user("metadata-check@example.com", "N3w$MetaPass!24")
            user = db.query(User).filter(User.id == created.id).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.password_hash_scheme, "argon2")
            self.assertIsNotNone(user.password_hash_updated_at)

    def test_successful_login_can_upgrade_password_hash(self):
        with SessionLocal() as db:
            service = UserService(db)
            user = service.get_user_by_email(self.email)
            self.assertIsNotNone(user)
            old_hash = user.hashed_password

            with patch("scripts.server.services.user_service.password_hash_needs_upgrade", return_value=True):
                authed_user = service.authenticate_user(self.email, self.password)

            self.assertIsNotNone(authed_user)
            db.refresh(user)
            self.assertNotEqual(user.hashed_password, old_hash)
            self.assertEqual(user.password_hash_scheme, "argon2")
            self.assertIsNotNone(user.password_hash_updated_at)

    def test_signup_persists_local_identity_and_profile(self):
        res = self.client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newsignup@example.com",
                "password": "Str0ng!Pass#77",
                "username": "new_signup",
                "full_name": "New Signup",
                "phone_number": "+1 (555) 999-0000",
                "signup_source": "web",
            },
            headers={"User-Agent": "AuthHardeningTests/1.0"},
        )
        self.assertEqual(res.status_code, 200)

        with SessionLocal() as db:
            user = db.query(User).filter(User.email == "newsignup@example.com").first()
            self.assertIsNotNone(user)

            identity = (
                db.query(AuthIdentity)
                .filter(AuthIdentity.user_id == user.id, AuthIdentity.provider == "local")
                .first()
            )
            self.assertIsNotNone(identity)
            self.assertEqual(identity.provider_user_id, "newsignup@example.com")
            self.assertEqual(identity.provider_email, "newsignup@example.com")

            profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            self.assertIsNotNone(profile)
            self.assertEqual(profile.username, "new_signup")
            self.assertEqual(profile.full_name, "New Signup")
            self.assertEqual(profile.signup_source, "web")

    def test_signup_rejects_duplicate_username(self):
        first = self.client.post(
            "/api/v1/auth/signup",
            json={
                "email": "firstuser@example.com",
                "password": "Str0ng!Pass#77",
                "username": "shared_name",
            },
        )
        self.assertEqual(first.status_code, 200)

        second = self.client.post(
            "/api/v1/auth/signup",
            json={
                "email": "seconduser@example.com",
                "password": "An0ther!Pass#88",
                "username": "shared_name",
            },
        )
        self.assertEqual(second.status_code, 400)
        self.assertIn("Username already taken", second.json().get("detail", ""))


if __name__ == "__main__":
    unittest.main()
