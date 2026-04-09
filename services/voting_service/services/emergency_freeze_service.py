from __future__ import annotations

from contextlib import closing
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Protocol

from services.audit_service import WORMLogger
from services.voting_service.models.emergency_freeze import EmergencyFreezeEvent
from services.voting_service.models.election_state import ElectionState


class EmergencyFreezeHistoryStore(Protocol):
    """Persistence abstraction for emergency-freeze history."""

    def append(self, event: EmergencyFreezeEvent) -> None:
        """Persist a freeze-history event."""

    def history(self, election_id: str | None = None) -> list[EmergencyFreezeEvent]:
        """Return freeze-history events, optionally filtered by election."""


class InMemoryEmergencyFreezeHistoryStore:
    """Volatile freeze-history store for tests and ephemeral runtimes."""

    def __init__(self) -> None:
        self._events: list[EmergencyFreezeEvent] = []

    def append(self, event: EmergencyFreezeEvent) -> None:
        self._events.append(event)

    def history(self, election_id: str | None = None) -> list[EmergencyFreezeEvent]:
        if election_id is None:
            return list(self._events)
        return [event for event in self._events if event.election_id == election_id]


class SQLiteEmergencyFreezeHistoryStore:
    """Durable emergency-freeze history store backed by SQLite."""

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
                CREATE TABLE IF NOT EXISTS emergency_freeze_events (
                    sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    election_id TEXT NOT NULL,
                    activated INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    approvals INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def append(self, event: EmergencyFreezeEvent) -> None:
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    """
                    INSERT INTO emergency_freeze_events
                    (election_id, activated, reason, approvals, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        event.election_id,
                        int(event.activated),
                        event.reason,
                        event.approvals,
                        event.created_at.isoformat(),
                    ),
                )
                connection.commit()

    def history(self, election_id: str | None = None) -> list[EmergencyFreezeEvent]:
        query = """
            SELECT election_id, activated, reason, approvals, created_at
            FROM emergency_freeze_events
        """
        params: tuple[object, ...] = ()
        if election_id is not None:
            query += " WHERE election_id = ?"
            params = (election_id,)
        query += " ORDER BY sequence_id ASC"
        with closing(self._connect()) as connection:
            rows = connection.execute(query, params).fetchall()
        return [
            EmergencyFreezeEvent.from_record(
                election_id=row["election_id"],
                activated=row["activated"],
                reason=row["reason"],
                approvals=row["approvals"],
                created_at=row["created_at"],
            )
            for row in rows
        ]


class EmergencyFreezeService:
    def __init__(
        self,
        audit_logger: WORMLogger | None = None,
        history_store: EmergencyFreezeHistoryStore | None = None,
    ) -> None:
        self.audit_logger = audit_logger
        self.history_store = history_store or InMemoryEmergencyFreezeHistoryStore()

    @classmethod
    def with_sqlite_store(
        cls,
        database_path: str,
        *,
        audit_logger: WORMLogger | None = None,
    ) -> "EmergencyFreezeService":
        return cls(
            audit_logger=audit_logger,
            history_store=SQLiteEmergencyFreezeHistoryStore(database_path),
        )

    def _audit(self, event_type: str, state: ElectionState, reason: str, approvals: int) -> None:
        if self.audit_logger is None:
            return
        self.audit_logger.append(
            event_type,
            {
                "election_id": state.election_id,
                "phase": state.phase,
                "freeze_active": state.freeze_active,
                "reason": reason,
                "approvals": approvals,
            },
        )

    def _validate_approvals(self, approvals: int, *, operation: str) -> None:
        if approvals < 3:
            raise ValueError(f"Emergency freeze {operation} requires at least 3 approvals")
        if approvals > 5:
            raise ValueError(f"Emergency freeze {operation} allows at most 5 approvals")

    def activate(self, state: ElectionState, reason: str, approvals: int):
        try:
            self._validate_approvals(approvals, operation="activation")
        except ValueError:
            self._audit("emergency_freeze_rejected", state, reason, approvals)
            raise
        updated_state = ElectionState(election_id=state.election_id, phase=state.phase, freeze_active=True)
        event = EmergencyFreezeEvent.create(state.election_id, True, reason, approvals)
        self.history_store.append(event)
        self._audit("emergency_freeze_activated", updated_state, reason, approvals)
        return updated_state, event

    def deactivate(self, state: ElectionState, reason: str, approvals: int):
        try:
            self._validate_approvals(approvals, operation="deactivation")
        except ValueError:
            self._audit("emergency_freeze_release_rejected", state, reason, approvals)
            raise
        updated_state = ElectionState(election_id=state.election_id, phase=state.phase, freeze_active=False)
        event = EmergencyFreezeEvent.create(state.election_id, False, reason, approvals)
        self.history_store.append(event)
        self._audit("emergency_freeze_deactivated", updated_state, reason, approvals)
        return updated_state, event
