"""Approval tracking helpers."""

from __future__ import annotations

from contextlib import closing
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Protocol


@dataclass(frozen=True)
class ApprovalRecord:
    operation_id: str
    approver: str
    approval_count: int
    recorded_at: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ApprovalStore(Protocol):
    def approve(self, operation_id: str, approver: str) -> int:
        """Record an approval and return the distinct approval count."""

    def history(self, operation_id: str | None = None) -> list[ApprovalRecord]:
        """Return approval history, optionally scoped to one operation."""


@dataclass
class InMemoryApprovalStore:
    approvals: dict[str, set[str]] = field(default_factory=dict)
    records: list[ApprovalRecord] = field(default_factory=list)

    def approve(self, operation_id: str, approver: str) -> int:
        approvers = self.approvals.setdefault(operation_id, set())
        if approver in approvers:
            return len(approvers)
        approvers.add(approver)
        approval_count = len(approvers)
        self.records.append(
            ApprovalRecord(
                operation_id=operation_id,
                approver=approver,
                approval_count=approval_count,
                recorded_at=datetime.now(timezone.utc).isoformat(),
            )
        )
        return approval_count

    def history(self, operation_id: str | None = None) -> list[ApprovalRecord]:
        if operation_id is None:
            return list(self.records)
        return [record for record in self.records if record.operation_id == operation_id]


class SQLiteApprovalStore:
    """Durable approval tracking store backed by SQLite."""

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
                CREATE TABLE IF NOT EXISTS operation_approvals (
                    operation_id TEXT NOT NULL,
                    approver TEXT NOT NULL,
                    PRIMARY KEY (operation_id, approver)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS approval_records (
                    sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id TEXT NOT NULL,
                    approver TEXT NOT NULL,
                    approval_count INTEGER NOT NULL,
                    recorded_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def approve(self, operation_id: str, approver: str) -> int:
        with self._lock:
            with closing(self._connect()) as connection:
                cursor = connection.execute(
                    """
                    INSERT OR IGNORE INTO operation_approvals (operation_id, approver)
                    VALUES (?, ?)
                    """,
                    (operation_id, approver),
                )
                approval_count = int(
                    connection.execute(
                        "SELECT COUNT(*) FROM operation_approvals WHERE operation_id = ?",
                        (operation_id,),
                    ).fetchone()[0]
                )
                if cursor.rowcount:
                    connection.execute(
                        """
                        INSERT INTO approval_records (operation_id, approver, approval_count, recorded_at)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            operation_id,
                            approver,
                            approval_count,
                            datetime.now(timezone.utc).isoformat(),
                        ),
                    )
                connection.commit()
        return approval_count

    def history(self, operation_id: str | None = None) -> list[ApprovalRecord]:
        query = """
            SELECT operation_id, approver, approval_count, recorded_at
            FROM approval_records
        """
        params: tuple[object, ...] = ()
        if operation_id is not None:
            query += " WHERE operation_id = ?"
            params = (operation_id,)
        query += " ORDER BY sequence_id ASC"
        with closing(self._connect()) as connection:
            rows = connection.execute(query, params).fetchall()
        return [
            ApprovalRecord(
                operation_id=row["operation_id"],
                approver=row["approver"],
                approval_count=row["approval_count"],
                recorded_at=row["recorded_at"],
            )
            for row in rows
        ]


@dataclass
class ApprovalTracker:
    store: ApprovalStore = field(default_factory=InMemoryApprovalStore)

    @classmethod
    def with_sqlite_store(cls, database_path: str) -> "ApprovalTracker":
        return cls(store=SQLiteApprovalStore(database_path))

    def approve(self, operation_id: str, approver: str) -> int:
        return self.store.approve(operation_id, approver)

    def history(self, operation_id: str | None = None) -> list[ApprovalRecord]:
        return self.store.history(operation_id)
