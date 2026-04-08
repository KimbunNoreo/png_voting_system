"""Audit helpers for election phase transitions."""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Protocol

from election_state.cryptographic_time_lock import build_time_lock_commitment


@dataclass(frozen=True)
class PhaseChangeAuditRecord:
    election_id: str
    previous_phase: str
    next_phase: str
    changed_by: tuple[str, ...]
    changed_at: str
    approvals: int
    commitment: str

    @classmethod
    def from_record(
        cls,
        *,
        election_id: str,
        previous_phase: str,
        next_phase: str,
        changed_by: str,
        changed_at: str,
        approvals: int,
        commitment: str,
    ) -> "PhaseChangeAuditRecord":
        return cls(
            election_id=election_id,
            previous_phase=previous_phase,
            next_phase=next_phase,
            changed_by=tuple(item for item in changed_by.split(",") if item),
            changed_at=changed_at,
            approvals=int(approvals),
            commitment=commitment,
        )


def record_phase_change(
    election_id: str,
    previous_phase: str,
    next_phase: str,
    approvers: tuple[str, ...],
) -> PhaseChangeAuditRecord:
    if len(approvers) < 2:
        raise ValueError("Phase changes require at least two approvers")
    changed_at = datetime.now(timezone.utc).isoformat()
    commitment = build_time_lock_commitment(election_id, next_phase, changed_at)
    return PhaseChangeAuditRecord(
        election_id=election_id,
        previous_phase=previous_phase,
        next_phase=next_phase,
        changed_by=approvers,
        changed_at=changed_at,
        approvals=len(approvers),
        commitment=commitment,
    )


class PhaseAuditStore(Protocol):
    """Persistence abstraction for election phase changes."""

    def append(self, record: PhaseChangeAuditRecord) -> None:
        """Persist a phase-change audit record."""

    def history(self, election_id: str) -> list[PhaseChangeAuditRecord]:
        """Return phase-change history for an election."""


class InMemoryPhaseAuditStore:
    """Volatile phase-audit store for tests and ephemeral runtimes."""

    def __init__(self) -> None:
        self._records: list[PhaseChangeAuditRecord] = []

    def append(self, record: PhaseChangeAuditRecord) -> None:
        self._records.append(record)

    def history(self, election_id: str) -> list[PhaseChangeAuditRecord]:
        return [record for record in self._records if record.election_id == election_id]


class SQLitePhaseAuditStore:
    """Durable phase-audit store backed by SQLite."""

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
                CREATE TABLE IF NOT EXISTS phase_change_audit (
                    sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    election_id TEXT NOT NULL,
                    previous_phase TEXT NOT NULL,
                    next_phase TEXT NOT NULL,
                    changed_by TEXT NOT NULL,
                    changed_at TEXT NOT NULL,
                    approvals INTEGER NOT NULL,
                    commitment TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def append(self, record: PhaseChangeAuditRecord) -> None:
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    """
                    INSERT INTO phase_change_audit
                    (election_id, previous_phase, next_phase, changed_by, changed_at, approvals, commitment)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.election_id,
                        record.previous_phase,
                        record.next_phase,
                        ",".join(record.changed_by),
                        record.changed_at,
                        record.approvals,
                        record.commitment,
                    ),
                )
                connection.commit()

    def history(self, election_id: str) -> list[PhaseChangeAuditRecord]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT election_id, previous_phase, next_phase, changed_by, changed_at, approvals, commitment
                FROM phase_change_audit
                WHERE election_id = ?
                ORDER BY sequence_id ASC
                """,
                (election_id,),
            ).fetchall()
        return [PhaseChangeAuditRecord.from_record(**dict(row)) for row in rows]


class PhaseChangeAuditor:
    """Records election phase transitions into a persistent audit store."""

    def __init__(self, store: PhaseAuditStore | None = None) -> None:
        self.store = store or InMemoryPhaseAuditStore()

    @classmethod
    def with_sqlite_store(cls, database_path: str) -> "PhaseChangeAuditor":
        return cls(store=SQLitePhaseAuditStore(database_path))

    def record(
        self,
        election_id: str,
        previous_phase: str,
        next_phase: str,
        approvers: tuple[str, ...],
    ) -> PhaseChangeAuditRecord:
        record = record_phase_change(election_id, previous_phase, next_phase, approvers)
        self.store.append(record)
        return record

    def history(self, election_id: str) -> list[PhaseChangeAuditRecord]:
        return self.store.history(election_id)
