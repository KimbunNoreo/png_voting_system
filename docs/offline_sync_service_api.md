# Offline Sync Service API

This document describes the standalone Phase 1 offline sync runtime exposed by `python manage.py run-offline-sync 127.0.0.1:8100`.

## Runtime Start

Start the service locally:

```bash
python manage.py run-offline-sync 127.0.0.1:8100
```

Or with `make`:

```bash
make run-offline-sync
```

## Authentication

- `GET /health` and `GET /ready` do not require authentication.
- All `/api/v1/offline-sync/*` endpoints require `Authorization: Bearer admin-...`.
- In the current runtime, any bearer token beginning with `admin-` is accepted as an operator token.

Example:

```http
Authorization: Bearer admin-operator-1
```

The runtime returns the stripped operator token as `admin_token` in authenticated responses.

## Health And Readiness

### `GET /health`

Liveness probe.

Example response:

```json
{
  "status": "ok",
  "service": "offline_sync_service",
  "phase": "phase1"
}
```

### `GET /ready`

Readiness probe with queue and approval-store metadata.

Example response:

```json
{
  "status": "ready",
  "service": "offline_sync_service",
  "phase": "phase1",
  "queue_depth": 0,
  "approval_store": "InMemoryApprovalStore",
  "operation_store": "InMemoryOfflineSyncOperationHistoryStore"
}
```

## Operator Endpoints

### `POST /api/v1/offline-sync/stage`

Stages one sanitized offline record into the local queue.

Request body:

```json
{
  "record": {
    "token_hash": "t1",
    "created_at": "2026-04-08T00:00:00Z",
    "sub": "citizen-1"
  }
}
```

Example response:

```json
{
  "admin_token": "operator-1",
  "queue_depth": 1,
  "record": {
    "token_hash": "t1",
    "created_at": "2026-04-08T00:00:00Z",
    "sub": "[redacted]"
  }
}
```

Notes:

- Sensitive fields are sanitized before queueing.
- The action is audited as `offline_sync_record_staged`.

### `GET /api/v1/offline-sync/queue`

Returns the currently queued sanitized records.

Example response:

```json
{
  "admin_token": "operator-1",
  "queue_depth": 1,
  "queued_records": [
    {
      "token_hash": "t1",
      "created_at": "2026-04-08T00:00:00Z",
      "sub": "[redacted]"
    }
  ]
}
```

Notes:

- The action is audited as `offline_sync_queue_inspected`.

### `POST /api/v1/offline-sync/flush`

Flushes the queued records against a remote batch, produces signed reconciliation artifacts, and empties the queue on success.

Request body:

```json
{
  "device_id": "device-1",
  "remote_records": [
    {
      "token_hash": "t1",
      "created_at": "2026-04-08T00:01:00Z"
    }
  ],
  "approvers": [
    "official-1",
    "official-2"
  ]
}
```

Example response:

```json
{
  "admin_token": "operator-1",
  "queue_depth": 0,
  "artifacts": {
    "manifest": {
      "device_id": "device-1",
      "record_count": 1,
      "digest": "sha256:example",
      "signature": "base64-signature"
    },
    "conflict_report": {
      "conflict_count": 1,
      "decisions": [
        {
          "token_hash": "t1",
          "resolution": "remote_rejected_duplicate"
        }
      ]
    }
  },
  "manifest_valid": true
}
```

Notes:

- The manifest is signed with the Phase 1 RSA-4096 signing flow and then verified before the response is returned.
- `manifest_valid` must be `true` for a successful signed flush.
- The action is audited as `offline_sync_flushed`.

Approval rules:

- Flushes with no detected conflicts require 1 approval.
- Flushes with one or more conflicts require 2 unique approvers.
- If the provided approvers are insufficient, the service rejects the request and audits `offline_sync_flush_rejected`.

Example rejection shape:

```json
{
  "error": "Offline sync flush requires at least 2 unique approvals"
}
```

### `GET /api/v1/offline-sync/approvals`

Returns recorded approval history. The runtime accepts `operation_id` in the JSON body when narrowing the results.

Request body:

```json
{
  "operation_id": "4d76d7d4..."
}
```

Example response:

```json
{
  "admin_token": "operator-1",
  "approvals": [
    {
      "operation_id": "4d76d7d4...",
      "approver": "official-1",
      "approved_at": "2026-04-08T00:01:00Z"
    },
    {
      "operation_id": "4d76d7d4...",
      "approver": "official-2",
      "approved_at": "2026-04-08T00:01:01Z"
    }
  ]
}
```

Notes:

- `operation_id` is deterministic for a reconciliation batch.
- Approval history can be backed by the durable SQLite approval tracker in configured environments.

### `GET /api/v1/offline-sync/operations`

Returns recorded signed flush history. The runtime accepts `operation_id` in the JSON body when narrowing the results.

Request body:

```json
{
  "operation_id": "4d76d7d4..."
}
```

Example response:

```json
{
  "admin_token": "operator-1",
  "operations": [
    {
      "operation_id": "4d76d7d4...",
      "operator_id": "operator-1",
      "device_id": "device-1",
      "manifest_digest": "sha256:example",
      "manifest_signature": "base64-signature",
      "record_count": 1,
      "conflict_count": 1,
      "manifest_valid": true,
      "approvals": [
        "official-1",
        "official-2"
      ],
      "conflict_report": {
        "merged_count": 1,
        "conflict_count": 1,
        "decisions": [
          {
            "token_hash": "t1",
            "winner_created_at": "2026-04-08T00:00:00Z",
            "discarded_created_at": "2026-04-08T00:01:00Z",
            "resolution": "keep_earliest"
          }
        ]
      },
      "recorded_at": "2026-04-08T00:01:02Z"
    }
  ]
}
```

Notes:

- This history survives restarts when the durable SQLite operation-history store is enabled.
- The record preserves manifest integrity metadata, approval attribution, and conflict evidence for operator review.

### `GET /api/v1/offline-sync/operations/export`

Returns a signed export of offline sync operation history for auditors and legal review.

Example response:

```json
{
  "admin_token": "operator-1",
  "export": {
    "payload": "{\"operations\":[...],\"phase\":\"phase1\",\"service\":\"offline_sync_service\"}",
    "signature": "base64-signature"
  }
}
```

Notes:

- The payload is sanitized before signing.
- The signature uses the Phase 1 RSA-4096 signing flow.
- By default the runtime signs with the selected device key for the requested `device_id`.

### `GET /api/v1/offline-sync/operations/evidence-bundle`

Builds a court-ready evidence bundle around the signed offline sync export.

Example response:

```json
{
  "admin_token": "operator-1",
  "bundle": {
    "case_id": "case-offline-review",
    "artifacts": [
      {
        "artifact_id": "case-offline-review-offline-sync-export",
        "kind": "offline_sync_export",
        "service": "offline_sync_service",
        "phase": "phase1",
        "operations": [],
        "signature": "base64-signature",
        "metadata": {
          "case_id": "case-offline-review",
          "actor": "operator-1",
          "artifact_role": "offline_sync_reconciliation"
        }
      }
    ],
    "custody_events": [
      {
        "actor": "operator-1",
        "action": "offline_sync_export_signed",
        "timestamp": "2026-04-08T00:01:02Z"
      },
      {
        "actor": "operator-1",
        "action": "bundle_created",
        "timestamp": "2026-04-08T00:01:03Z"
      }
    ],
    "verification_statement": "Evidence package for case case-offline-review has been verified."
  }
}
```

Notes:

- This wraps the signed offline sync export in bundle metadata and chain-of-custody records.
- The bundle is intended for compliance review, auditor handoff, and court-ready packaging.

### `GET /api/v1/offline-sync/status`

Returns an operator summary of the running service.

Example response:

```json
{
  "admin_token": "operator-1",
  "report": {
    "status": "ok",
    "service": "offline_sync_service",
    "phase": "phase1",
    "queue_depth": 1,
    "approval_store": "InMemoryApprovalStore",
    "operation_store": "InMemoryOfflineSyncOperationHistoryStore",
    "approval_history_count": 0,
    "latest_approval": null,
    "operation_history_count": 1,
    "offline_sync_conflict_total": 1,
    "latest_operation": {
      "operation_id": "4d76d7d4...",
      "operator_id": "operator-1",
      "device_id": "device-1",
      "manifest_digest": "sha256:example",
      "manifest_signature": "base64-signature",
      "record_count": 1,
      "conflict_count": 1,
      "manifest_valid": true,
      "approvals": [
        "official-1",
        "official-2"
      ],
      "conflict_report": {
        "merged_count": 1,
        "conflict_count": 1,
        "decisions": []
      },
      "recorded_at": "2026-04-08T00:01:02Z"
    },
    "latest_audit_event": "offline_sync_evidence_bundle_generated",
    "latest_evidence_event": "offline_sync_evidence_bundle_generated"
  }
}
```

## Failure Semantics

- Missing or malformed admin bearer token returns `403`.
- Invalid JSON, missing required fields, or unsupported request shapes return `400`.
- Unexpected runtime failures return `500`.

## Operational Notes

- Queue contents, conflict diagnostics, and audit payloads are sanitized before storage or export.
- Offline sync operator actions participate in the tamper-evident WORM audit chain.
- Successful signed flushes are recorded into operation history with manifest digest, signature, approval set, and conflict report.
- Conflict-heavy flushes are intended to be reviewed under multi-person control before reconciliation is committed.
