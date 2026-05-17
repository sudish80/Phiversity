import os
import subprocess
import sys
import time
import unittest
from pathlib import Path

from test import _test_env  # Ensures test DB env vars are configured before imports.

from scripts.server.database import Base, SessionLocal, engine
from scripts.server.models import JobModel, PasswordResetToken, RefreshToken, RevokedAccessToken, User
from scripts.server.services import job_service as job_service_module
from scripts.server.services.job_service import JobService


ROOT = Path(__file__).resolve().parents[1]


class OperationalGuardrailsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.temp_root = Path(_test_env.TEST_ROOT) / "operational"
        cls.temp_root.mkdir(parents=True, exist_ok=True)

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

    def test_database_guard_rejects_sqlite_in_production_like_env(self):
        env = os.environ.copy()
        env["DATABASE_URL"] = "sqlite:///phase2-guard.db"
        env["PHIVERSITY_ENV"] = "production"
        env.pop("ALLOW_SQLITE_IN_PRODUCTION", None)

        result = subprocess.run(
            [sys.executable, "-c", "import scripts.server.database"],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "SQLite is disabled in production-like environments",
            result.stdout + result.stderr,
        )

    def test_database_guard_allows_sqlite_in_development(self):
        env = os.environ.copy()
        env["DATABASE_URL"] = "sqlite:///phase2-dev-ok.db"
        env["PHIVERSITY_ENV"] = "development"
        env.pop("ALLOW_SQLITE_IN_PRODUCTION", None)

        result = subprocess.run(
            [sys.executable, "-c", "import scripts.server.database; print('database-ok')"],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("database-ok", result.stdout)

    def test_app_import_requires_schema_ready_in_production_mode(self):
        env = os.environ.copy()
        env["DATABASE_URL"] = "sqlite:///phase3-schema-guard.db"
        env["PHIVERSITY_ENV"] = "production"
        env["REQUIRE_DB_MIGRATIONS"] = "true"
        env["ALLOW_SQLITE_IN_PRODUCTION"] = "true"

        result = subprocess.run(
            [sys.executable, "-c", "import scripts.server.app"],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Run Alembic migrations before starting the service", result.stdout + result.stderr)

    def test_job_slot_limit_blocks_second_claim_until_timeout(self):
        previous = os.environ.get("MAX_CONCURRENT_JOBS")
        os.environ["MAX_CONCURRENT_JOBS"] = "1"
        start = time.monotonic()

        try:
            self.assertTrue(job_service_module._acquire_job_slot(1))
            self.assertFalse(job_service_module._acquire_job_slot(1))
        finally:
            job_service_module._release_job_slot()
            if previous is None:
                os.environ.pop("MAX_CONCURRENT_JOBS", None)
            else:
                os.environ["MAX_CONCURRENT_JOBS"] = previous

        self.assertGreaterEqual(time.monotonic() - start, 1)

    def test_run_and_capture_returns_timeout_code(self):
        out_dir = self.temp_root / "job-timeout"
        out_dir.mkdir(parents=True, exist_ok=True)

        with SessionLocal() as db:
            job = JobModel(
                id="timeout-job",
                status="running",
                out_dir=str(out_dir),
                log="",
            )
            db.add(job)
            db.commit()
            db.refresh(job)

            service = JobService(db)
            rc = service._run_and_capture(
                [sys.executable, "-c", "import time; time.sleep(2)"],
                ROOT,
                job,
                db=db,
                timeout_seconds=1,
            )

            db.refresh(job)

        self.assertEqual(rc, 124)
        self.assertIn("timed out", job.log.lower())


if __name__ == "__main__":
    unittest.main()
