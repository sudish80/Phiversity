# Disaster Recovery Runbook

## Purpose
This runbook defines recovery steps for service outage, data corruption, credential compromise, and region-level disruption for Phiversity.

## Recovery Targets
- RTO (Recovery Time Objective): 4 hours
- RPO (Recovery Point Objective): 15 minutes

## Critical Assets
- API service and worker processes
- Primary application database
- Media storage bucket/filesystem
- JWT key material and security secrets
- Audit/security event logs

## Incident Severity
- SEV1: Production unavailable or data loss in progress
- SEV2: Core auth/generation degraded
- SEV3: Partial feature impact

## Immediate Triage Checklist
1. Declare incident and assign incident commander.
2. Freeze risky deployments and schema changes.
3. Capture current system state (logs, metrics, queue depth, DB health).
4. Notify stakeholders (engineering, security, operations).

## Backup Policy
- Database snapshots every 15 minutes; keep 30 days.
- Daily encrypted full backup; keep 90 days.
- Weekly immutable offsite backup; keep 12 months.
- JWT keyring and env secrets backed up to secure secret manager.

## Recovery Procedures
### 1. API Service Outage
1. Scale replacement instances from latest known-good image.
2. Restore environment secrets and verify SECRET_KEY/JWT keyring.
3. Run health checks:
- `/health`
- `/api/v1/auth/me` with known test token
4. Re-enable traffic gradually.

### 2. Database Corruption or Loss
1. Put API in maintenance mode (read-only if possible).
2. Identify last clean snapshot within RPO.
3. Restore snapshot to recovery database.
4. Run migration/schema validation and integrity checks.
5. Point API to restored DB and run smoke tests.
6. Resume writes and monitor for data drift.

### 3. Credential or Signing Key Compromise
1. Rotate compromised secrets immediately.
2. Force JWT key rotation and revoke all refresh token families.
3. Invalidate API keys and reissue to impacted clients.
4. Trigger security event notifications and audit export.
5. Require password reset or MFA re-verification if needed.

### 4. Storage Loss (media artifacts)
1. Restore object storage from last consistent snapshot.
2. Rebuild missing generated artifacts by replaying queued jobs when possible.
3. Validate signed URLs and access controls.

## Validation After Recovery
1. Run authentication hardening test suite.
2. Validate core video generation pipeline end-to-end.
3. Confirm audit and security events ingestion.
4. Confirm backup jobs resume and next snapshot succeeds.

## Communication Templates
- Internal update cadence: every 30 minutes during SEV1.
- External status page updates: every 60 minutes or on major milestone.

## Post-Incident Actions
1. Complete root-cause analysis within 5 business days.
2. Track corrective actions with owners and due dates.
3. Update this runbook with discovered gaps.

## Quarterly Disaster Recovery Drill
1. Restore latest backup to isolated environment.
2. Run functional smoke tests and auth hardening tests.
3. Measure actual RTO/RPO and document deviations.
4. File remediation tasks for unmet targets.
