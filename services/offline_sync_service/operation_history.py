"""Durable operation history for offline synchronization flushes."""

from __future__ import annotations

from contextlib import closing
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import sqlite3
from threading import Lock
from typing import Protocol


@dataclass(frozen=True)
class OfflineSyncOperationRecord:
    operation_id: str
    operator_id: str
    device_id: str
    manifest_digest: str
    manifest_signature: str
    record_count: int
    conflict_count: int
    manifest_valid: bool
    approvals: tuple[str, ...]
    conflict_report: dict[str, object]
    recorded_at: str

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["approvals"] = list(self.approvals)
        return payload


class OfflineSyncOperationHistoryStore(Protocol):
    """Storage contract for offline sync operation history."""

    def append(self, record: OfflineSyncOperationRecord) -> None:
        """Persist one operation record."""

    def history(self, operation_id: str | None = None) -> list[OfflineSyncOperationRecord]:
        """Return all operation records, optionally scoped to one operation."""


@dataclass
class InMemoryOfflineSyncOperationHistoryStore:
    records: list[OfflineSyncOperationRecord] = field(default_factory=list)

    def append(self, record: OfflineSyncOperationRecord) -> None:
        self.records.append(record)

    def history(self, operation_id: str | None = None) -> list[OfflineSyncOperationRecord]:
        if operation_id is None:
            return list(self.records)
        return [record for record in self.records if record.operation_id == operation_id]


class SQLiteOfflineSyncOperationHistoryStore:
    """SQLite-backed history for signed offline sync operations."""

    def __init__(self, database_path: str) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.database_path))
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS offline_sync_operation_history (
                    sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id TEXT NOT NULL,
                    operator_id TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    manifest_digest TEXT NOT NULL,
                    manifest_signature TEXT NOT NULL,
                    record_count INTEGER NOT NULL,
                    conflict_count INTEGER NOT NULL,
                    manifest_valid INTEGER NOT NULL,
                    approvals_json TEXT NOT NULL,
                    conflict_report_json TEXT NOT NULL,
                    recorded_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def append(self, record: OfflineSyncOperationRecord) -> None:
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    """
                    INSERT INTO offline_sync_operation_history (
                        operation_id,
                        operator_id,
                        device_id,
                        manifest_digest,
                        manifest_signature,
                        record_count,
                        conflict_count,
                        manifest_valid,
                        approvals_json,
                        conflict_report_json,
                        recorded_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.operation_id,
                        record.operator_id,
                        record.device_id,
                        record.manifest_digest,
                        record.manifest_signature,
                        record.record_count,
                        record.conflict_count,
                        int(record.manifest_valid),
                        json.dumps(list(record.approvals)),
                        json.dumps(record.conflict_report),
                        record.recorded_at,
                    ),
                )
                connection.commit()

    def history(self, operation_id: str | None = None) -> list[OfflineSyncOperationRecord]:
        query = """
            SELECT
                operation_id,
                operator_id,
                device_id,
                manifest_digest,
                manifest_signature,
                record_count,
                conflict_count,
                manifest_valid,
                approvals_json,
                conflict_report_json,
                recorded_at
            FROM offline_sync_operation_history
        """
        params: tuple[object, ...] = ()
        if operation_id is not None:
            query += " WHERE operation_id = ?"
            params = (operation_id,)
        query += " ORDER BY sequence_id ASC"
        with closing(self._connect()) as connection:
            rows = connection.execute(query, params).fetchall()
        return [
            OfflineSyncOperationRecord(
                operation_id=row["operation_id"],
                operator_id=row["operator_id"],
                device_id=row["device_id"],
                manifest_digest=row["manifest_digest"],
                manifest_signature=row["manifest_signature"],
                record_count=row["record_count"],
                conflict_count=row["conflict_count"],
                manifest_valid=bool(row["manifest_valid"]),
                approvals=tuple(json.loads(row["approvals_json"])),
                conflict_report=dict(json.loads(row["conflict_report_json"])),
                recorded_at=row["recorded_at"],
            )
            for row in rows
        ]


@dataclass
class OfflineSyncOperationHistory:
    store: OfflineSyncOperationHistoryStore = field(default_factory=InMemoryOfflineSyncOperationHistoryStore)

    @classmethod
    def with_sqlite_store(cls, database_path: str) -> "OfflineSyncOperationHistory":
        return cls(store=SQLiteOfflineSyncOperationHistoryStore(database_path))

    def append(
        self,
        *,
        operation_id: str,
        operator_id: str,
        device_id: str,
        manifest_digest: str,
        manifest_signature: str,
        record_count: int,
        conflict_count: int,
        manifest_valid: bool,
        approvals: tuple[str, ...],
        conflict_report: dict[str, object],
    ) -> None:
        self.store.append(
            OfflineSyncOperationRecord(
                operation_id=operation_id,
                operator_id=operator_id,
                device_id=device_id,
                manifest_digest=manifest_digest,
                manifest_signature=manifest_signature,
                record_count=record_count,
                conflict_count=conflict_count,
                manifest_valid=manifest_valid,
                approvals=approvals,
                conflict_report=conflict_report,
                recorded_at=datetime.now(timezone.utc).isoformat(),
            )
        )

    def history(self, operation_id: str | None = None) -> list[OfflineSyncOperationRecord]:
        return self.store.history(operation_id)
