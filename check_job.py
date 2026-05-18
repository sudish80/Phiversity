import os, sys
sys.path.insert(0, '.')
os.environ['DATABASE_URL'] = 'sqlite:///media/database/phiversity.db'
os.environ['ALLOW_SQLITE_IN_PRODUCTION'] = 'true'
from scripts.server.database import SessionLocal
from scripts.server.models import JobModel
from datetime import datetime, timezone

db = SessionLocal()
try:
    job = db.query(JobModel).filter(JobModel.id == 'a8aafc7d-b403-4724-a331-fc552db01cdb').first()
    if job:
        now = datetime.now(timezone.utc)
        print(f'Status: {job.status}')
        print(f'Progress: {job.progress}')
        print(f'Created: {job.created_at}')
        print(f'Started: {job.started_at}')
        if job.created_at:
            age_min = (now.replace(tzinfo=None) - job.created_at.replace(tzinfo=None)).total_seconds() / 60
            print(f'Age: {age_min:.1f} min')
        if job.started_at:
            run_min = (now.replace(tzinfo=None) - job.started_at.replace(tzinfo=None)).total_seconds() / 60
            print(f'Running for: {run_min:.1f} min')
        print(f'Worker: {job.worker_id}')
        print(f'Log length: {len(job.log or "")} chars')
        log = job.log or ''
        if log:
            lines = log.strip().splitlines()
            print(f'Last 10 log lines:')
            for l in lines[-10:]:
                print(f'  {l}')
    else:
        print('Job not found')
finally:
    db.close()
