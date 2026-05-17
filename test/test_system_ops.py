import unittest
from datetime import timedelta
from unittest.mock import patch

from test import _test_env  # Ensures test DB env vars are configured before imports.

from fastapi.testclient import TestClient

import scripts.server.app as app_module
from scripts.server.app import app
from scripts.server.auth import create_access_token, get_password_hash
from scripts.server.database import SessionLocal, engine
from scripts.server.models import JobModel, PasswordResetToken, RefreshToken, RevokedAccessToken, User, UserProfile, UserRole
from scripts.server.services.job_service import _utcnow


class SystemOpsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        engine.dispose()

    def setUp(self):
        with SessionLocal() as db:
            db.query(UserProfile).delete()
            db.query(JobModel).delete()
            db.query(PasswordResetToken).delete()
            db.query(RefreshToken).delete()
            db.query(RevokedAccessToken).delete()
            db.query(User).delete()
            db.commit()

            admin = User(
                email="admin@example.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.ADMIN,
            )
            member = User(
                email="member@example.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.USER,
            )
            db.add_all([admin, member])
            db.commit()
            db.refresh(admin)
            db.refresh(member)

            queued_job = JobModel(
                id="queued-job",
                status="queued",
                progress=0,
                request_payload='{"problem": "queued"}',
            )
            running_job = JobModel(
                id="running-job",
                status="running",
                progress=35,
                request_payload='{"problem": "running"}',
                worker_id="worker-1",
                lease_expires_at=_utcnow() - timedelta(seconds=10),
            )
            error_job = JobModel(
                id="error-job",
                status="error",
                progress=20,
                request_payload='{"problem": "error"}',
            )
            db.add_all([queued_job, running_job, error_job])
            db.commit()

            admin_profile = UserProfile(
                user_id=admin.id,
                username="admin_profile",
                signup_source="admin_seed",
                signup_ip="127.0.0.1",
                signup_user_agent="SystemOpsTests/Admin",
            )
            member_profile = UserProfile(
                user_id=member.id,
                username="member_profile",
                signup_source="web",
                signup_ip="127.0.0.2",
                signup_user_agent="SystemOpsTests/Member",
            )
            db.add_all([admin_profile, member_profile])
            db.commit()

            self.admin_email = admin.email
            self.member_email = member.email

    def _auth_headers(self, email: str) -> dict:
        token = create_access_token(data={"sub": email})
        return {"Authorization": f"Bearer {token}"}

    def test_queue_health_requires_admin(self):
        res = self.client.get(
            "/api/v1/system/queue-health",
            headers=self._auth_headers(self.member_email),
        )
        self.assertEqual(res.status_code, 403)

    def test_queue_health_reports_queue_metrics_for_admin(self):
        res = self.client.get(
            "/api/v1/system/queue-health",
            headers=self._auth_headers(self.admin_email),
        )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn(data["job_execution_mode"], {"inline", "worker"})
        self.assertEqual(data["queued_jobs"], 1)
        self.assertEqual(data["running_jobs"], 1)
        self.assertEqual(data["error_jobs"], 1)
        self.assertEqual(data["stale_leased_jobs"], 1)
        self.assertIsNotNone(data["oldest_queued_job_age_seconds"])

    def test_admin_system_diagnostics_requires_admin(self):
        res = self.client.get(
            "/api/v1/admin/system/diagnostics",
            headers=self._auth_headers(self.member_email),
        )
        self.assertEqual(res.status_code, 403)

    def test_admin_system_diagnostics_reports_expected_sections(self):
        res = self.client.get(
            "/api/v1/admin/system/diagnostics",
            headers=self._auth_headers(self.admin_email),
        )

        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("timestamp", data)
        self.assertFalse(data["include_sensitive"])
        self.assertIn("database", data)
        self.assertIn("queue", data)
        self.assertIn("key_auth", data)

        self.assertIn("schema_readiness_required", data["database"])
        self.assertIn("schema_ready", data["database"])
        self.assertIn("missing_schema_count", data["database"])
        self.assertNotIn("missing_schema_items", data["database"])

        self.assertEqual(data["queue"]["queued_jobs"], 1)
        self.assertEqual(data["queue"]["running_jobs"], 1)
        self.assertEqual(data["queue"]["error_jobs"], 1)

        self.assertTrue(data["key_auth"]["secret_key_configured"])
        self.assertEqual(data["key_auth"]["jwt_algorithm"], "HS256")
        self.assertTrue(data["key_auth"]["csrf_enabled"])
        self.assertNotIn("jwt_current_kid", data["key_auth"])
        self.assertNotIn("csrf_protected_paths", data["key_auth"])

    def test_admin_system_diagnostics_include_sensitive_true(self):
        res = self.client.get(
            "/api/v1/admin/system/diagnostics",
            params={"include_sensitive": "true"},
            headers=self._auth_headers(self.admin_email),
        )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["include_sensitive"])

        self.assertIn("missing_schema_items", data["database"])
        self.assertIsInstance(data["database"]["missing_schema_items"], list)
        self.assertIn("jwt_current_kid", data["key_auth"])
        self.assertIn("csrf_protected_paths", data["key_auth"])
        self.assertIn("/api/v1/auth/refresh", data["key_auth"]["csrf_protected_paths"])
        self.assertIn("/api/v1/auth/logout", data["key_auth"]["csrf_protected_paths"])

    def test_admin_storage_health_requires_admin(self):
        res = self.client.get(
            "/api/v1/admin/system/storage-health",
            headers=self._auth_headers(self.member_email),
        )
        self.assertEqual(res.status_code, 403)

    def test_admin_storage_health_reports_local_backend_state(self):
        class LocalStorage:
            backend = "local"

        with patch.object(app_module, "cloud_storage", LocalStorage()):
            res = self.client.get(
                "/api/v1/admin/system/storage-health",
                headers=self._auth_headers(self.admin_email),
            )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("timestamp", data)
        self.assertEqual(data["storage"]["backend"], "local")
        self.assertFalse(data["storage"]["is_cloud_backend"])
        self.assertFalse(data["s3"]["check_performed"])
        self.assertIsNone(data["s3"]["connected"])

    def test_admin_storage_health_runs_quick_s3_check(self):
        class FakeS3Client:
            @staticmethod
            def head_bucket(Bucket):
                return {"ResponseMetadata": {"HTTPStatusCode": 200}}

        class S3Storage:
            backend = "s3"
            bucket_name = "test-bucket"
            s3_client = FakeS3Client()

        with patch.object(app_module, "cloud_storage", S3Storage()):
            res = self.client.get(
                "/api/v1/admin/system/storage-health",
                headers=self._auth_headers(self.admin_email),
            )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["storage"]["backend"], "s3")
        self.assertTrue(data["storage"]["is_cloud_backend"])
        self.assertTrue(data["s3"]["check_performed"])
        self.assertTrue(data["s3"]["connected"])
        self.assertIsNotNone(data["s3"]["latency_ms"])
        self.assertIsNone(data["s3"]["error"])

    def test_admin_signup_profiles_requires_admin(self):
        res = self.client.get(
            "/api/v1/admin/signup-profiles",
            headers=self._auth_headers(self.member_email),
        )
        self.assertEqual(res.status_code, 403)

    def test_admin_signup_profiles_returns_profile_data(self):
        res = self.client.get(
            "/api/v1/admin/signup-profiles",
            headers=self._auth_headers(self.admin_email),
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("profiles", data)
        self.assertGreaterEqual(data["total"], 2)
        self.assertGreaterEqual(data["count"], 2)

        usernames = {row.get("username") for row in data["profiles"]}
        self.assertIn("admin_profile", usernames)
        self.assertIn("member_profile", usernames)

        row = next((p for p in data["profiles"] if p.get("username") == "member_profile"), None)
        self.assertIsNotNone(row)
        self.assertEqual(row.get("signup_source"), "web")
        self.assertEqual(row.get("signup_user_agent"), "SystemOpsTests/Member")


if __name__ == "__main__":
    unittest.main()
