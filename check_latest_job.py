import os, sys
sys.path.insert(0, '.')
os.environ['DATABASE_URL'] = 'sqlite:///media/database/phiversity.db'
os.environ['ALLOW_SQLITE_IN_PRODUCTION'] = 'true'
from scripts.server.database import SessionLocal
from scripts.server.models import JobModel
db = SessionLocal()
try:
    job = db.query(JobModel).order_by(JobModel.created_at.desc()).first()
    if job:
        print(f'ID: {job.id}')
        print(f'Status: {job.status} Progress: {job.progress}')
        print(f'Created: {job.created_at}')
        print(f'Out dir: {job.out_dir}')
        log = job.log or ''
        print(f'Log lines: {len(log.splitlines())}')
        for l in log.strip().splitlines()[-5:]:
            print(f'  {l}')
        if job.out_dir:
            import pathlib
            d = pathlib.Path(job.out_dir)
            files = list(d.iterdir()) if d.exists() else []
            print(f'Files: {[f.name for f in files]}')
    else:
        print('No jobs')
finally:
    db.close()
