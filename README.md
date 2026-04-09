# SecureVote PNG

Phase 1 implementation scaffold for a zero-trust, offline-first electronic voting system integrated with an external National ID service.

## Core Guarantees

- Identity data is handled only by the external NID system.
- The voting domain stores only token hashes, encrypted votes, signatures, and audit metadata.
- Phase 1 uses AES-256-GCM and RSA-4096 only.
- AI, homomorphic encryption, and zero-knowledge proofs remain disabled.

## Implemented Core

- `config/`: typed settings and security policy
- `services/nid_client/`: external NID validation boundary
- `services/voting_service/`: encrypted vote flow and anti-replay controls
- `services/api_gateway/`: zero-trust request pipeline
- `services/offline_sync_service/`: offline queueing and merge logic
- `services/audit_service/`: hash-chained append-only audit logging
- `time_sync/`, `election_state/`, `legal_evidence/`, `public_verification/`

## Local Use

```bash
python manage.py show-config
python manage.py check-phase1
python manage.py readiness-check core
python manage.py runserver 127.0.0.1:8000
python manage.py run-offline-sync 127.0.0.1:8100
python -m unittest
docker-compose up --build
```

## Runtime Entrypoints

- Gateway and voting demo runtime: `python manage.py runserver 127.0.0.1:8000`
- Standalone offline sync service: `python manage.py run-offline-sync 127.0.0.1:8100`
- Shared endpoint inventory:
  - `python manage.py list-endpoints`
  - `python manage.py list-endpoints --markdown`
- Readiness profiles:
  - `python manage.py readiness-check quick`
  - `python manage.py readiness-check core`
  - `python manage.py readiness-check full`
- Make targets:
  - `make run`
  - `make run-offline-sync`
  - `make readiness`
  - `make readiness-quick`
  - `make readiness-full`

## Offline Sync Service

The offline sync service now runs as its own operator-facing HTTP surface with Phase 1 controls:

- `GET /health`
  Returns liveness only.
- `GET /ready`
  Returns readiness plus queue depth and approval-store mode.
- `POST /api/v1/offline-sync/stage`
  Stages one sanitized offline record.
- `GET /api/v1/offline-sync/queue`
  Returns current queued records.
- `POST /api/v1/offline-sync/flush`
  Flushes queued records, emits a signed sync manifest, and produces a conflict report.
- `GET /api/v1/offline-sync/approvals`
  Returns approval history for a reconciliation batch.
- `GET /api/v1/offline-sync/operations`
  Returns durable signed flush history including manifest integrity metadata and conflict reports.
- `GET /api/v1/offline-sync/operations/export`
  Returns a signed sanitized export of offline sync operation history for auditors and evidence workflows.
- `GET /api/v1/offline-sync/operations/evidence-bundle`
  Returns a court-ready evidence bundle built from the signed offline sync export and custody metadata.
- `GET /api/v1/offline-sync/status`
  Returns queue depth, approval and operation history counts, store types, and latest audited offline sync event.

All offline sync admin endpoints require `Authorization: Bearer admin-...` in the current runtime. Conflict-heavy flushes require 2 unique approvers.

For concrete request and response examples, see `docs/offline_sync_service_api.md`.

## Compliance And Evidence

- `GET /api/v1/vote/compliance/report`
  Returns audit-chain health plus offline sync reconciliation posture.
- `GET /api/v1/vote/compliance/offline-sync-evidence`
  Returns an observer-facing evidence bundle for offline sync reconciliation review.
- `GET /api/v1/offline-sync/operations/export`
  Returns a signed sanitized export of offline sync operation history.
- `GET /api/v1/offline-sync/operations/evidence-bundle`
  Returns a court-ready evidence bundle from the standalone offline sync service.

## Deployment Notes

- `docker-compose.yml` now includes:
  - `app` on port `8000`
  - `offline-sync-service` on port `8100`
- `kubernetes/offline-sync-service.yaml` now runs `python manage.py run-offline-sync 0.0.0.0:8100`
- The offline sync service uses `/ready` for readiness and `/health` for liveness
