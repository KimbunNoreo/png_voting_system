# Offline Sync And Verification Notes

## Standalone Offline Sync Runtime

Start the service locally:

```bash
python manage.py run-offline-sync 127.0.0.1:8100
```

Or with `make`:

```bash
make run-offline-sync
```

## Operator Endpoints

- `GET /health`
  Liveness check.
- `GET /ready`
  Readiness check with queue depth and approval-store mode.
- `POST /api/v1/offline-sync/stage`
  Add a sanitized offline record to the queue.
- `GET /api/v1/offline-sync/queue`
  Inspect queued offline records.
- `POST /api/v1/offline-sync/flush`
  Perform reconciliation, emit a signed manifest, and return a conflict report.
- `GET /api/v1/offline-sync/approvals`
  Query approval history for a specific reconciliation batch.
- `GET /api/v1/offline-sync/status`
  Summary view for operators including queue depth, approval history count, and latest audited offline sync event.

## Approval Rules

- Normal flushes require 1 approval.
- Conflict-heavy flushes require 2 unique approvers.
- Approval history is tracked with a deterministic `operation_id`.

## Security Notes

- Staged and merged records are sanitized before storage and queueing.
- Sync manifests are signed with Phase 1 RSA-4096 signing.
- Conflict reports preserve token-hash-based reconciliation evidence without reintroducing identity fields.
- Offline sync operator actions are audited through the hash-chained audit logger.
