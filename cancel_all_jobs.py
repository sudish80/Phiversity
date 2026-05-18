import os, sys
sys.path.insert(0, '.')
os.environ['DATABASE_URL'] = 'sqlite:///media/database/phiversity.db'
os.environ['ALLOW_SQLITE_IN_PRODUCTION'] = 'true'
from scripts.server.database import SessionLocal
from scripts.server.models import JobModel
from datetime import datetime, timezone
db = SessionLocal()
try:
    now = datetime.now(timezone.utc)
    active = db.query(JobModel).filter(JobModel.status.in_(['queued', 'running'])).all()
    print(f'Found {len(active)} active jobs to cancel')
    for j in active:
        j.status = 'cancelled'
        j.progress = 0
        j.finished_at = now
        j.log = (j.log or '') + f'\n{now.isoformat()} | Cancelled by user'
        print(f'  {j.id} -> cancelled')
    db.commit()
finally:
    db.close()
