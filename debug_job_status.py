import os, sys, json
sys.path.insert(0, '.')
os.environ['DATABASE_URL'] = 'sqlite:///media/database/phiversity.db'
os.environ['ALLOW_SQLITE_IN_PRODUCTION'] = 'true'
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['JWT_SECRET'] = 'test-jwt-secret'
os.environ['AUTH_DB_PATH'] = 'media/database/phiversity.db'

from scripts.server.database import SessionLocal
from scripts.server.models import JobModel
from scripts.server.services.job_service import JobService
from scripts.server.app import _job_artifact_urls
from scripts.server.schemas import JobStatusResponse

db = SessionLocal()
try:
    service = JobService(db)

    job = db.query(JobModel).filter(JobModel.user_id.isnot(None)).first()
    if not job:
        print("No job with user_id found")
        # Create one
        user = db.query(User).first()
        if user:
            job = service.create_job()
            job.user_id = user.id
            db.commit()
            print(f"Created test job: {job.id}")
        else:
            print("No user found either, cannot test")

    if job:
        print(f"Job: {job.id}")
        print(f"  status: {job.status!r}")
        print(f"  user_id: {job.user_id}")
        print(f"  progress: {job.progress} (type: {type(job.progress).__name__})")
        print(f"  log length: {len(job.log or '')}")
        print(f"  out_dir: {job.out_dir!r}")
        print(f"  video_path: {job.video_path!r}")
        print(f"  has error_message attr: {hasattr(job, 'error_message')}")

        try:
            urls = _job_artifact_urls(job)
            print(f"URLs: {urls}")
        except Exception as e:
            print(f"ERROR in _job_artifact_urls: {e}")
            import traceback
            traceback.print_exc()
            urls = {"video_url": None, "plan_url": None, "log_url": None}

        try:
            summary = service.extract_job_summary(job)
            print(f"Summary: {summary}")
        except Exception as e:
            print(f"ERROR in extract_job_summary: {e}")
            summary = None

        log_content = job.log or ""
        if len(log_content) > 10000:
            log_content = "..." + log_content[-10000:]

        err_msg = getattr(job, "error_message", None) or None

        response_data = {
            "status": job.status,
            "log": log_content,
            "progress": job.progress,
            "video_url": urls["video_url"],
            "plan_url": urls["plan_url"],
            "log_url": urls["log_url"],
            "summary": summary,
            "error": err_msg,
        }

        print(f"\nResponse data keys: {list(response_data.keys())}")
        for k, v in response_data.items():
            print(f"  {k}: {v!r} (type: {type(v).__name__})")

        try:
            validated = JobStatusResponse(**response_data)
            print(f"\nPydantic validation: OK")
        except Exception as e:
            print(f"\nPydantic validation ERROR: {e}")
            import traceback
            traceback.print_exc()
finally:
    db.close()
