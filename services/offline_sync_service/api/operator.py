"""Reusable operator API for offline sync staging and signed flushes."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

from human_factors.multi_person_auth.approval_tracking import ApprovalTracker
from human_factors.multi_person_auth.session_requirements import required_approvals
from services.audit_service import WORMLogger
from services.offline_sync_service.operation_history import OfflineSyncOperationHistory
from services.offline_sync_service.sync.conflict_resolution import resolve_conflicts_with_report
from services.offline_sync_service.sync.engine import SyncEngine
from services.offline_sync_service.sync.sync_manifest import SyncManifest, verify_sync_manifest


@dataclass
class OfflineSyncOperatorAPI:
    """Thin service facade around offline sync queue and flush operations."""

    engine: SyncEngine
    audit_logger: WORMLogger | None = None
    approval_tracker: ApprovalTracker | None = None
    operation_log: OfflineSyncOperationHistory | None = None

    def __post_init__(self) -> None:
        if self.approval_tracker is None:
            self.approval_tracker = ApprovalTracker()
        if self.operation_log is None:
            self.operation_log = OfflineSyncOperationHistory()

    def _audit(self, event_type: str, payload: dict[str, object]) -> None:
        if self.audit_logger is not None:
            self.audit_logger.append(event_type, payload)

    def _operation_id(self, device_id: str, remote_records: list[dict[str, object]]) -> str:
        token_hashes = sorted(
            str(record.get("token_hash", ""))
            for record in (self.engine.local_store.fetch_all() + remote_records)
            if "token_hash" in record
        )
        canonical = f"{device_id}:{'|'.join(token_hashes)}"
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def stage_record(self, record: dict[str, object], *, operator_id: str | None = None) -> dict[str, object]:
        self.engine.stage_vote(record)
        result = {
            "queue_depth": len(self.engine.queue),
            "record": self.engine.queue.peek_all()[-1],
        }
        self._audit(
            "offline_sync_record_staged",
            {
                "operator_id": operator_id or "system",
                "queue_depth": result["queue_depth"],
                "token_hash": result["record"].get("token_hash"),
                "created_at": result["record"].get("created_at"),
            },
        )
        return result

    def queue_status(self, *, operator_id: str | None = None) -> dict[str, object]:
        result = {
            "queue_depth": len(self.engine.queue),
            "queued_records": self.engine.queue.peek_all(),
        }
        self._audit(
            "offline_sync_queue_inspected",
            {
                "operator_id": operator_id or "system",
                "queue_depth": result["queue_depth"],
            },
        )
        return result

    def flush(
        self,
        *,
        remote_records: list[dict[str, object]],
        device_id: str,
        private_key_pem: str,
        public_key_pem: str,
        operator_id: str | None = None,
        approvers: tuple[str, ...] = (),
    ) -> dict[str, object]:
        _, preflight_report = resolve_conflicts_with_report(self.engine.local_store.fetch_all(), remote_records)
        required = 1
        if preflight_report.conflict_count > 0:
            required = required_approvals("offline_sync_conflict_flush")
        unique_approvers = tuple(sorted(set(approvers)))
        operation_id = self._operation_id(device_id, remote_records)
        if self.approval_tracker is not None:
            for approver in unique_approvers:
                self.approval_tracker.approve(operation_id, approver)
        if len(unique_approvers) < required:
            self._audit(
                "offline_sync_flush_rejected",
                {
                    "operation_id": operation_id,
                    "operator_id": operator_id or "system",
                    "device_id": device_id,
                    "provided_approvals": len(unique_approvers),
                    "required_approvals": required,
                    "conflict_count": preflight_report.conflict_count,
                },
            )
            raise ValueError(f"Offline sync flush requires at least {required} unique approvals")
        artifacts = self.engine.flush_with_artifacts(
            remote_records,
            device_id=device_id,
            private_key_pem=private_key_pem,
        )
        manifest_valid = verify_sync_manifest(SyncManifest(**artifacts["manifest"]), public_key_pem)
        result = {
            "queue_depth": len(self.engine.queue),
            "artifacts": artifacts,
            "manifest_valid": manifest_valid,
        }
        if self.operation_log is not None:
            self.operation_log.append(
                operation_id=operation_id,
                operator_id=operator_id or "system",
                device_id=device_id,
                manifest_digest=str(artifacts["manifest"]["digest"]),
                manifest_signature=str(artifacts["manifest"]["signature"]),
                record_count=int(artifacts["manifest"]["record_count"]),
                conflict_count=int(artifacts["conflict_report"]["conflict_count"]),
                manifest_valid=manifest_valid,
                approvals=unique_approvers,
                conflict_report=dict(artifacts["conflict_report"]),
            )
        self._audit(
            "offline_sync_flushed",
            {
                "operation_id": operation_id,
                "operator_id": operator_id or "system",
                "device_id": device_id,
                "queue_depth": result["queue_depth"],
                "manifest_valid": manifest_valid,
                "record_count": artifacts["manifest"]["record_count"],
                "conflict_count": artifacts["conflict_report"]["conflict_count"],
                "manifest_digest": artifacts["manifest"]["digest"],
                "approvals": len(unique_approvers),
            },
        )
        return result

    def approval_history(self, operation_id: str | None = None) -> list[dict[str, object]]:
        return [record.to_dict() for record in self.approval_tracker.history(operation_id)]

    def operation_history(self, operation_id: str | None = None) -> list[dict[str, object]]:
        return [record.to_dict() for record in self.operation_log.history(operation_id)]
