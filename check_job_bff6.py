import os, sys
sys.path.insert(0, '.')
os.environ['DATABASE_URL'] = 'sqlite:///media/database/phiversity.db'
os.environ['ALLOW_SQLITE_IN_PRODUCTION'] = 'true'
from scripts.server.database import SessionLocal
from scripts.server.models import JobModel
db = SessionLocal()
try:
    job = db.query(JobModel).filter(JobModel.id.like('bff6%')).first()
    if job:
        print(f'ID: {job.id}')
        print(f'Status: {job.status} Progress: {job.progress}')
        print(f'Created: {job.created_at}')
        print(f'Out dir: {job.out_dir}')
        log = job.log or ''
        print(f'Log lines: {len(log.splitlines())}')
        for l in log.strip().splitlines()[-5:]:
            print(f'  {l}')
    else:
        print('bff6 job not found')
    
    # Also show all jobs
    jobs = db.query(JobModel).order_by(JobModel.created_at.desc()).limit(5).all()
    print(f'\nLast {len(jobs)} jobs:')
    for j in jobs:
        print(f'  {j.id} | {j.status:10} | progress={j.progress} | created={j.created_at}')
finally:
    db.close()
