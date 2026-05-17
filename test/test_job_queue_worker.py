import os
import unittest
from datetime import timedelta

from test import _test_env  # Ensures test DB env vars are configured before imports.

from scripts.server.database import Base, SessionLocal, engine
from scripts.server.models import JobModel, PasswordResetToken, RefreshToken, RevokedAccessToken, User
from scripts.server.services.job_service import JobService, _utcnow


class JobQueueWorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure schema exists for this test module regardless of import order.
        Base.metadata.create_all(bind=engine)

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

    def test_start_background_job_in_worker_mode_enqueues_payload(self):
        previous = os.environ.get("JOB_EXECUTION_MODE")
        os.environ["JOB_EXECUTION_MODE"] = "worker"

        try:
            with SessionLocal() as db:
                service = JobService(db)
                job = service.create_job()
                service.start_background_job(
                    job.id,
                    {
                        "problem": "Integrate x^2",
                        "mode": "question_solving",
                        "orchestrate": True,
                    },
                )
                db.refresh(job)

                self.assertEqual(job.status, "queued")
                self.assertEqual(job.progress, 0)
                self.assertIsNone(job.worker_id)
                self.assertIn("Integrate x^2", job.request_payload or "")
                self.assertIn("worker execution mode", job.log)
        finally:
            if previous is None:
                os.environ.pop("JOB_EXECUTION_MODE", None)
            else:
                os.environ["JOB_EXECUTION_MODE"] = previous

    def test_claim_next_job_claims_oldest_queued_job(self):
        previous = os.environ.get("JOB_EXECUTION_MODE")
        os.environ["JOB_EXECUTION_MODE"] = "worker"

        try:
            with SessionLocal() as db:
                service = JobService(db)
                first = service.create_job()
                second = service.create_job()
                service.start_background_job(first.id, {"problem": "first", "orchestrate": False})
                service.start_background_job(second.id, {"problem": "second", "orchestrate": False})

                claimed = service.claim_next_job("worker-test")
                self.assertIsNotNone(claimed)
                self.assertEqual(claimed.id, first.id)

                db.refresh(first)
                db.refresh(second)
                self.assertEqual(first.status, "running")
                self.assertEqual(first.worker_id, "worker-test")
                self.assertEqual(first.attempt_count, 1)
                self.assertIsNotNone(first.claimed_at)
                self.assertIsNotNone(first.lease_expires_at)
                self.assertEqual(second.status, "queued")
        finally:
            if previous is None:
                os.environ.pop("JOB_EXECUTION_MODE", None)
            else:
                os.environ["JOB_EXECUTION_MODE"] = previous

    def test_recover_interrupted_jobs_requeues_stale_running_jobs(self):
        with SessionLocal() as db:
            service = JobService(db)
            job = service.create_job()
            job.status = "running"
            job.progress = 55
            job.request_payload = '{"problem": "stale"}'
            job.worker_id = "dead-worker"
            job.started_at = _utcnow()
            job.claimed_at = _utcnow()
            job.lease_expires_at = _utcnow() - timedelta(seconds=5)
            db.commit()

            recovered = service.recover_interrupted_jobs(reason="test recovery")
            self.assertEqual(recovered, 1)

            db.refresh(job)
            self.assertEqual(job.status, "queued")
            self.assertLessEqual(job.progress, 5)
            self.assertIsNone(job.worker_id)
            self.assertIsNone(job.started_at)
            self.assertIsNone(job.claimed_at)
            self.assertIsNone(job.lease_expires_at)
            self.assertIn("re-queued after test recovery", job.log)

    def test_error_flow_appends_summary_block(self):
        with SessionLocal() as db:
            service = JobService(db)
            job = service.create_job()
            job.started_at = _utcnow() - timedelta(seconds=8)
            db.commit()

            service._mark_job_error(
                job,
                "[server] Pipeline failed\n",
                stage="pipeline",
                exit_code=124,
                next_action_hint="Inspect pipeline command output",
                stage_durations_seconds={"pipeline": 5},
            )
            db.refresh(job)

            self.assertIn("=== JOB SUMMARY ===", job.log)
            self.assertIn("failed_stage: pipeline", job.log)
            self.assertIn("exit_code: 124", job.log)
            self.assertIn("total_duration_seconds:", job.log)
            self.assertIn("next_action_hint: Inspect pipeline command output", job.log)

    def test_success_summary_block_contains_stage_durations(self):
        with SessionLocal() as db:
            service = JobService(db)
            job = service.create_job()
            job.started_at = _utcnow() - timedelta(seconds=10)
            db.commit()

            service._append_job_summary(
                job,
                status="done",
                failed_stage="none",
                exit_code=0,
                total_duration_seconds=10,
                stage_durations_seconds={"orchestration": 3, "pipeline": 6},
                next_action_hint="No action required.",
            )
            db.refresh(job)

            self.assertIn("=== JOB SUMMARY ===", job.log)
            self.assertIn("status: done", job.log)
            self.assertIn("failed_stage: none", job.log)
            self.assertIn('"orchestration": 3', job.log)
            self.assertIn('"pipeline": 6', job.log)


if __name__ == "__main__":
    unittest.main()
