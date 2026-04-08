"""Compliance reporting for audit data."""

from __future__ import annotations

from services.audit_service.detection.tamper import verify_hash_chain
from services.audit_service.logger.worm_logger import WORMLogger


def generate_compliance_report(
    logger: WORMLogger,
    *,
    offline_sync_operations: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    entries = logger.entries()
    operations = offline_sync_operations or []
    latest_evidence_event = next(
        (
            entry.event_type
            for entry in reversed(entries)
            if entry.event_type in {"offline_sync_operation_exported", "offline_sync_evidence_bundle_generated"}
        ),
        None,
    )
    return {
        "entry_count": len(entries),
        "hash_chain_valid": verify_hash_chain(entries),
        "latest_event": entries[-1].event_type if entries else None,
        "offline_sync_operation_count": len(operations),
        "offline_sync_conflict_total": sum(int(operation.get("conflict_count", 0)) for operation in operations),
        "latest_offline_sync_operation_id": operations[-1]["operation_id"] if operations else None,
        "latest_evidence_event": latest_evidence_event,
    }
