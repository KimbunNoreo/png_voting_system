"""Offline sync dependency assembly for operator-facing workflows."""

from __future__ import annotations

from dataclasses import dataclass

from config import get_settings
from human_factors.multi_person_auth.approval_tracking import ApprovalTracker
from services.offline_sync_service.operation_history import OfflineSyncOperationHistory
from services.audit_service import WORMLogger
from services.offline_sync_service.api.operator import OfflineSyncOperatorAPI
from services.offline_sync_service.sync.engine import SyncEngine


@dataclass(frozen=True)
class OfflineSyncDependencies:
    """Runtime dependency bundle for offline sync operations."""

    engine: SyncEngine
    approval_tracker: ApprovalTracker
    operation_history: OfflineSyncOperationHistory
    operator_api: OfflineSyncOperatorAPI
    audit_logger: WORMLogger | None


def build_offline_sync_dependencies(
    *,
    audit_logger: WORMLogger | None = None,
    force_in_memory: bool = False,
) -> OfflineSyncDependencies:
    """Build the offline-sync dependency graph from central settings."""

    settings = get_settings().offline_sync_service
    engine = SyncEngine()
    if settings.use_durable_approval_tracker and not force_in_memory:
        approval_tracker = ApprovalTracker.with_sqlite_store(settings.approval_tracker_path)
    else:
        approval_tracker = ApprovalTracker()
    if settings.use_durable_operation_history and not force_in_memory:
        operation_history = OfflineSyncOperationHistory.with_sqlite_store(settings.operation_history_path)
    else:
        operation_history = OfflineSyncOperationHistory()
    operator_api = OfflineSyncOperatorAPI(
        engine,
        audit_logger=audit_logger,
        approval_tracker=approval_tracker,
        operation_log=operation_history,
    )
    return OfflineSyncDependencies(
        engine=engine,
        approval_tracker=approval_tracker,
        operation_history=operation_history,
        operator_api=operator_api,
        audit_logger=audit_logger,
    )
