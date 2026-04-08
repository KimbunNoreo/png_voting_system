"""Offline synchronization engine."""

from __future__ import annotations

from dataclasses import dataclass, field

from services.offline_sync_service.local_db.encrypted_store import EncryptedStore
from services.offline_sync_service.sync.conflict_resolution import resolve_conflicts, resolve_conflicts_with_report
from services.offline_sync_service.sync.queue import SyncQueue
from services.offline_sync_service.sync.sync_manifest import build_sync_manifest


@dataclass
class SyncEngine:
    """Coordinates queue draining and conflict-safe synchronization."""

    local_store: EncryptedStore = field(default_factory=EncryptedStore)
    queue: SyncQueue = field(default_factory=SyncQueue)

    def stage_vote(self, record: dict[str, object]) -> None:
        self.local_store.insert(record)
        self.queue.push(record)

    def flush(self, remote_records: list[dict[str, object]]) -> list[dict[str, object]]:
        merged = resolve_conflicts(self.local_store.fetch_all(), remote_records)
        self.local_store.clear()
        for record in merged:
            self.local_store.insert(record)
        while len(self.queue):
            self.queue.pop()
        return merged

    def flush_with_artifacts(
        self,
        remote_records: list[dict[str, object]],
        *,
        device_id: str,
        private_key_pem: str,
    ) -> dict[str, object]:
        """Flush queued records and emit signed reconciliation artifacts."""

        merged, conflict_report = resolve_conflicts_with_report(self.local_store.fetch_all(), remote_records)
        manifest = build_sync_manifest(device_id, merged, private_key_pem)
        self.local_store.clear()
        for record in merged:
            self.local_store.insert(record)
        while len(self.queue):
            self.queue.pop()
        return {
            "records": merged,
            "manifest": manifest.to_dict(),
            "conflict_report": conflict_report.to_dict(),
        }
