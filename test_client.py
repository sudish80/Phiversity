import os, sys
sys.path.insert(0, '.')
os.environ['DATABASE_URL'] = 'sqlite:///media/database/phiversity.db'
os.environ['ALLOW_SQLITE_IN_PRODUCTION'] = 'true'
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['JWT_SECRET'] = 'test-jwt-secret'
os.environ['AUTH_DB_PATH'] = 'media/database/phiversity.db'

from fastapi.testclient import TestClient
from scripts.server.app import app

client = TestClient(app)

# Guest login
resp = client.post('/api/v1/auth/guest')
print(f'Guest: {resp.status_code}')
guest = resp.json()
token = guest['access_token']
headers = {'Authorization': f'Bearer {token}'}

# List jobs
resp = client.get('/api/v1/jobs', headers=headers)
print(f'List jobs: {resp.status_code} {resp.json()}')

# Submit a job
body = {'problem': 'What is 2+2?', 'mode': 'question_solving'}
resp = client.post('/api/v1/run', headers=headers, json=body)
print(f'Run: {resp.status_code}')
job = resp.json()
jid = job['job_id']
print(f"Job ID: {jid} status: {job['status']}")

# Get job status
resp = client.get(f'/api/v1/jobs/{jid}', headers=headers)
print(f'Status: {resp.status_code}')
if resp.status_code == 500:
    print(f'Response text: {resp.text[:1000]}')
else:
    print(f'Response: {resp.json()}')
