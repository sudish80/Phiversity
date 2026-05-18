import os, sys
sys.path.insert(0, '.')
os.environ['DATABASE_URL'] = 'sqlite:///media/database/phiversity.db'
os.environ['ALLOW_SQLITE_IN_PRODUCTION'] = 'true'
from scripts.server.database import SessionLocal
from scripts.server.models import JobModel
from datetime import datetime, timezone
db = SessionLocal()
try:
    jid = 'bff6e723-f89b-4119-be5e-9a4e4a69a190'
    job = db.query(JobModel).filter(JobModel.id == jid).first()
    if job:
        job.status = 'cancelled'
        job.progress = 0
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        print(f'Job {jid} cancelled')
    else:
        print('Job not found')
finally:
    db.close()
