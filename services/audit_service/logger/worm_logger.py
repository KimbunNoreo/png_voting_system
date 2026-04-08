"""Write-once style audit logger with hash chaining."""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Protocol

from services.audit_service.payload_sanitizer import sanitize_audit_payload


@dataclass(frozen=True)
class AuditEntry:
    timestamp: str
    event_type: str
    payload: dict[str, object]
    previous_hash: str
    entry_hash: str

    @classmethod
    def from_record(
        cls,
        *,
        timestamp: str,
        event_type: str,
        payload: str,
        previous_hash: str,
        entry_hash: str,
    ) -> "AuditEntry":
        return cls(
            timestamp=timestamp,
            event_type=event_type,
            payload=json.loads(payload),
            previous_hash=previous_hash,
            entry_hash=entry_hash,
        )


class AuditStore(Protocol):
    """Persistence abstraction for append-only audit chains."""

    def append(self, entry: AuditEntry) -> None:
        """Persist a fully formed audit entry."""

    def entries(self) -> list[AuditEntry]:
        """Return the complete ordered audit chain."""


class InMemoryAuditStore:
    """Volatile store used for unit tests and ephemeral runtimes."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def append(self, entry: AuditEntry) -> None:
        self._entries.append(entry)

    def entries(self) -> list[AuditEntry]:
        return list(self._entries)


class SQLiteAuditStore:
    """Durable append-only audit store backed by SQLite."""

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
                CREATE TABLE IF NOT EXISTS audit_entries (
                    sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL UNIQUE
                )
                """
            )
            connection.commit()

    def append(self, entry: AuditEntry) -> None:
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    """
                    INSERT INTO audit_entries (timestamp, event_type, payload, previous_hash, entry_hash)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        entry.timestamp,
                        entry.event_type,
                        json.dumps(entry.payload, sort_keys=True, separators=(",", ":")),
                        entry.previous_hash,
                        entry.entry_hash,
                    ),
                )
                connection.commit()

    def entries(self) -> list[AuditEntry]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT timestamp, event_type, payload, previous_hash, entry_hash
                FROM audit_entries
                ORDER BY sequence_id ASC
                """
            ).fetchall()
        return [
            AuditEntry.from_record(
                timestamp=row["timestamp"],
                event_type=row["event_type"],
                payload=row["payload"],
                previous_hash=row["previous_hash"],
                entry_hash=row["entry_hash"],
            )
            for row in rows
        ]


@dataclass
class WORMLogger:
    """Maintains append-only entries linked by hash chain."""

    store: AuditStore = field(default_factory=InMemoryAuditStore)

    @classmethod
    def with_sqlite_store(cls, database_path: str) -> "WORMLogger":
        return cls(store=SQLiteAuditStore(database_path))

    def append(self, event_type: str, payload: dict[str, object]) -> AuditEntry:
        existing_entries = self.store.entries()
        previous_hash = existing_entries[-1].entry_hash if existing_entries else "GENESIS"
        timestamp = datetime.now(timezone.utc).isoformat()
        sanitized_payload = sanitize_audit_payload(payload)
        canonical = json.dumps(
            {
                "timestamp": timestamp,
                "event_type": event_type,
                "payload": sanitized_payload,
                "previous_hash": previous_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        entry_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        entry = AuditEntry(timestamp, event_type, sanitized_payload, previous_hash, entry_hash)
        self.store.append(entry)
        return entry

    def entries(self) -> list[AuditEntry]:
        return self.store.entries()
