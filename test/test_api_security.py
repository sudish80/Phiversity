import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from test._test_env import TEST_ROOT

from fastapi.testclient import TestClient

import scripts.server.app as app_module
from scripts.server.app import app
from scripts.server.auth import create_access_token, get_password_hash
from scripts.server.database import SessionLocal, engine
from scripts.server.models import JobModel, PasswordResetToken, RefreshToken, RevokedAccessToken, User, UserRole


class ApiSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.temp_root = Path(TEST_ROOT)

    @classmethod
    def tearDownClass(cls):
        engine.dispose()

    def setUp(self):
        with SessionLocal() as db:
            db.query(JobModel).delete()
            db.query(PasswordResetToken).delete()
            db.query(RefreshToken).delete()
            db.query(RevokedAccessToken).delete()
            db.query(User).delete()
            db.commit()

            owner = User(
                email="owner@example.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.USER,
            )
            other = User(
                email="other@example.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.USER,
            )
            db.add_all([owner, other])
            db.commit()
            db.refresh(owner)
            db.refresh(other)

            out_dir = self.temp_root / "job_artifacts"
            out_dir.mkdir(parents=True, exist_ok=True)
            video_path = out_dir / "final.mp4"
            plan_path = out_dir / "solution_plan.json"
            log_path = out_dir / "log.txt"
            video_path.write_bytes(b"fake video bytes")
            plan_path.write_text('{"ok": true}', encoding="utf-8")
            log_path.write_text("job completed", encoding="utf-8")

            job = JobModel(
                id="job-owner-1",
                status="done",
                progress=100,
                user_id=owner.id,
                out_dir=str(out_dir),
                video_path=str(video_path),
                plan_path=str(plan_path),
                log_path=str(log_path),
                video_url="/api/v1/jobs/job-owner-1/video",
                plan_url="/api/v1/jobs/job-owner-1/plan",
                log_url="/api/v1/jobs/job-owner-1/log",
            )
            db.add(job)
            db.commit()

            self.owner_email = owner.email
            self.other_email = other.email
            self.job_id = job.id

    def _auth_headers(self, email: str) -> dict:
        token = create_access_token(data={"sub": email})
        return {"Authorization": f"Bearer {token}"}

    def test_job_status_returns_protected_artifact_urls_for_owner(self):
        res = self.client.get(
            f"/api/v1/jobs/{self.job_id}",
            headers=self._auth_headers(self.owner_email),
        )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["video_url"], f"/api/v1/jobs/{self.job_id}/video")
        self.assertEqual(data["plan_url"], f"/api/v1/jobs/{self.job_id}/plan")
        self.assertEqual(data["log_url"], f"/api/v1/jobs/{self.job_id}/log")

    def test_job_status_includes_machine_readable_summary_when_present(self):
        summary_log = """
=== JOB SUMMARY ===
status: error
failed_stage: pipeline
exit_code: 124
total_duration_seconds: 23
stage_durations_seconds: {"pipeline": 21}
next_action_hint: Increase JOB_TIMEOUT or reduce rendering complexity.
===================
"""
        with SessionLocal() as db:
            db_job = db.query(JobModel).filter(JobModel.id == self.job_id).first()
            db_job.log = summary_log
            db.commit()

        res = self.client.get(
            f"/api/v1/jobs/{self.job_id}",
            headers=self._auth_headers(self.owner_email),
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("summary", data)
        self.assertEqual(data["summary"]["failed_stage"], "pipeline")
        self.assertEqual(data["summary"]["exit_code"], 124)

    def test_job_summary_endpoint_returns_compact_summary(self):
        summary_log = """
=== JOB SUMMARY ===
status: done
failed_stage: none
exit_code: 0
total_duration_seconds: 17
stage_durations_seconds: {"orchestration": 4, "pipeline": 11}
next_action_hint: No action required.
===================
"""
        with SessionLocal() as db:
            db_job = db.query(JobModel).filter(JobModel.id == self.job_id).first()
            db_job.log = summary_log
            db.commit()

        res = self.client.get(
            f"/api/v1/jobs/{self.job_id}/summary",
            headers=self._auth_headers(self.owner_email),
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "done")
        self.assertEqual(data["exit_code"], 0)
        self.assertIn("stage_durations_seconds", data)

    def test_job_status_hides_other_users_jobs(self):
        res = self.client.get(
            f"/api/v1/jobs/{self.job_id}",
            headers=self._auth_headers(self.other_email),
        )
        self.assertEqual(res.status_code, 404)

    def test_video_download_requires_job_ownership(self):
        owner_res = self.client.get(
            f"/api/v1/jobs/{self.job_id}/video",
            headers=self._auth_headers(self.owner_email),
        )
        other_res = self.client.get(
            f"/api/v1/jobs/{self.job_id}/video",
            headers=self._auth_headers(self.other_email),
        )

        self.assertEqual(owner_res.status_code, 200)
        self.assertEqual(owner_res.content, b"fake video bytes")
        self.assertEqual(other_res.status_code, 404)

    def test_legacy_status_route_no_longer_bypasses_auth(self):
        res = self.client.get(f"/api/jobs/{self.job_id}")
        self.assertEqual(res.status_code, 401)

    def test_status_does_not_expose_legacy_public_media_urls(self):
        with SessionLocal() as db:
            db_job = db.query(JobModel).filter(JobModel.id == self.job_id).first()
            db_job.video_url = "/media/videos/public.mp4"
            db_job.plan_url = "/media/texts/public-plan.json"
            db_job.log_url = "/media/videos/public-log.txt"
            db_job.plan_path = None
            db_job.log_path = None
            db.commit()

        res = self.client.get(
            f"/api/v1/jobs/{self.job_id}",
            headers=self._auth_headers(self.owner_email),
        )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse((data["video_url"] or "").startswith("/media"))
        self.assertFalse((data["plan_url"] or "").startswith("/media"))
        self.assertFalse((data["log_url"] or "").startswith("/media"))

    def test_job_status_returns_signed_urls_for_cloud_artifacts(self):
        with SessionLocal() as db:
            db_job = db.query(JobModel).filter(JobModel.id == self.job_id).first()
            db_job.video_path = "s3://test-bucket/videos/job-owner-1/final.mp4"
            db_job.plan_path = "s3://test-bucket/plans/job-owner-1/solution_plan.json"
            db.commit()

        class FakeCloudStorage:
            backend = "s3"

            @staticmethod
            def generate_signed_url(storage_ref: str, expires_in: int = 3600) -> str:
                return f"https://signed.example/{storage_ref.split('://', 1)[1]}?exp={expires_in}"

        with patch.object(app_module, "cloud_storage", FakeCloudStorage()):
            res = self.client.get(
                f"/api/v1/jobs/{self.job_id}",
                headers=self._auth_headers(self.owner_email),
            )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue((data["video_url"] or "").startswith("https://signed.example/test-bucket/videos/"))
        self.assertTrue((data["plan_url"] or "").startswith("https://signed.example/test-bucket/plans/"))

    def test_video_download_redirects_to_signed_cloud_url_for_owner(self):
        with SessionLocal() as db:
            db_job = db.query(JobModel).filter(JobModel.id == self.job_id).first()
            db_job.video_path = "s3://test-bucket/videos/job-owner-1/final.mp4"
            db.commit()

        class FakeCloudStorage:
            backend = "s3"

            @staticmethod
            def generate_signed_url(storage_ref: str, expires_in: int = 3600) -> str:
                return "https://signed.example/video.mp4"

        with patch.object(app_module, "cloud_storage", FakeCloudStorage()):
            owner_res = self.client.get(
                f"/api/v1/jobs/{self.job_id}/video",
                headers=self._auth_headers(self.owner_email),
                follow_redirects=False,
            )
            other_res = self.client.get(
                f"/api/v1/jobs/{self.job_id}/video",
                headers=self._auth_headers(self.other_email),
                follow_redirects=False,
            )

        self.assertEqual(owner_res.status_code, 307)
        self.assertEqual(owner_res.headers.get("location"), "https://signed.example/video.mp4")
        self.assertEqual(other_res.status_code, 404)

    def test_video_download_rejects_unsafe_path_outside_allowed_roots(self):
        unsafe_file = Path(tempfile.gettempdir()) / "phiversity-unsafe-video.mp4"
        unsafe_file.write_bytes(b"should not be downloadable")
        with SessionLocal() as db:
            db_job = db.query(JobModel).filter(JobModel.id == self.job_id).first()
            db_job.video_path = str(unsafe_file)
            db_job.out_dir = None
            db.commit()

        res = self.client.get(
            f"/api/v1/jobs/{self.job_id}/video",
            headers=self._auth_headers(self.owner_email),
        )
        self.assertEqual(res.status_code, 404)

    def test_plan_download_rejects_unsafe_path_outside_allowed_roots(self):
        unsafe_file = Path(tempfile.gettempdir()) / "phiversity-unsafe-plan.json"
        unsafe_file.write_text('{"unsafe": true}', encoding="utf-8")
        with SessionLocal() as db:
            db_job = db.query(JobModel).filter(JobModel.id == self.job_id).first()
            db_job.plan_path = str(unsafe_file)
            db.commit()

        res = self.client.get(
            f"/api/v1/jobs/{self.job_id}/plan",
            headers=self._auth_headers(self.owner_email),
        )
        self.assertEqual(res.status_code, 404)

    def test_log_download_rejects_unsafe_path_outside_allowed_roots(self):
        unsafe_file = Path(tempfile.gettempdir()) / "phiversity-unsafe-log.txt"
        unsafe_file.write_text("should not be downloadable", encoding="utf-8")
        with SessionLocal() as db:
            db_job = db.query(JobModel).filter(JobModel.id == self.job_id).first()
            db_job.log_path = str(unsafe_file)
            db_job.out_dir = None
            db.commit()

        res = self.client.get(
            f"/api/v1/jobs/{self.job_id}/log",
            headers=self._auth_headers(self.owner_email),
        )
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
