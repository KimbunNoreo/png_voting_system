"""Durable control-plane orchestration for election phase and freeze state."""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Protocol

from election_state.audit_phase_changes import PhaseChangeAuditRecord, PhaseChangeAuditor
from election_state.state_machine import ElectionStateMachine
from human_factors.multi_person_auth.freeze_authorization import freeze_allowed
from human_factors.multi_person_auth.session_requirements import required_approvals
from services.audit_service import WORMLogger


@dataclass(frozen=True)
class ElectionControlSnapshot:
    election_id: str
    phase: str
    freeze_active: bool
    freeze_reason: str = ""


class ElectionControlStore(Protocol):
    """Persistence abstraction for election control-plane state."""

    def save(self, snapshot: ElectionControlSnapshot) -> None:
        """Persist the current election control snapshot."""

    def load(self, election_id: str) -> ElectionControlSnapshot | None:
        """Load the current election control snapshot."""


class InMemoryElectionControlStore:
    """Volatile control-plane store for tests and ephemeral runtimes."""

    def __init__(self) -> None:
        self._snapshots: dict[str, ElectionControlSnapshot] = {}

    def save(self, snapshot: ElectionControlSnapshot) -> None:
        self._snapshots[snapshot.election_id] = snapshot

    def load(self, election_id: str) -> ElectionControlSnapshot | None:
        return self._snapshots.get(election_id)


class SQLiteElectionControlStore:
    """Durable control-plane store backed by SQLite."""

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
                CREATE TABLE IF NOT EXISTS election_control_state (
                    election_id TEXT PRIMARY KEY,
                    phase TEXT NOT NULL,
                    freeze_active INTEGER NOT NULL,
                    freeze_reason TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def save(self, snapshot: ElectionControlSnapshot) -> None:
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    """
                    INSERT INTO election_control_state (election_id, phase, freeze_active, freeze_reason)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(election_id) DO UPDATE SET
                        phase = excluded.phase,
                        freeze_active = excluded.freeze_active,
                        freeze_reason = excluded.freeze_reason
                    """,
                    (snapshot.election_id, snapshot.phase, int(snapshot.freeze_active), snapshot.freeze_reason),
                )
                connection.commit()

    def load(self, election_id: str) -> ElectionControlSnapshot | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT election_id, phase, freeze_active, freeze_reason
                FROM election_control_state
                WHERE election_id = ?
                """,
                (election_id,),
            ).fetchone()
        if row is None:
            return None
        return ElectionControlSnapshot(
            election_id=row["election_id"],
            phase=row["phase"],
            freeze_active=bool(row["freeze_active"]),
            freeze_reason=row["freeze_reason"],
        )


class ElectionControlPlane:
    """Approval-aware election control plane with durable phase/freeze state."""

    def __init__(
        self,
        initial_state: ElectionControlSnapshot,
        *,
        store: ElectionControlStore | None = None,
        phase_auditor: PhaseChangeAuditor | None = None,
        audit_logger: WORMLogger | None = None,
    ) -> None:
        self.store = store or InMemoryElectionControlStore()
        self.phase_auditor = phase_auditor or PhaseChangeAuditor()
        self.audit_logger = audit_logger
        existing_state = self.store.load(initial_state.election_id)
        if existing_state is None:
            self.store.save(initial_state)

    @classmethod
    def with_sqlite_store(
        cls,
        database_path: str,
        *,
        initial_state: ElectionControlSnapshot,
        audit_logger: WORMLogger | None = None,
        phase_audit_path: str | None = None,
    ) -> "ElectionControlPlane":
        return cls(
            initial_state=initial_state,
            store=SQLiteElectionControlStore(database_path),
            phase_auditor=PhaseChangeAuditor.with_sqlite_store(phase_audit_path or database_path),
            audit_logger=audit_logger,
        )

    def get_state(self, election_id: str) -> ElectionControlSnapshot:
        snapshot = self.store.load(election_id)
        if snapshot is None:
            raise ValueError("Election control state not found")
        return snapshot

    def _log(self, event_type: str, payload: dict[str, object]) -> None:
        if self.audit_logger is not None:
            self.audit_logger.append(event_type, payload)

    def transition_phase(self, election_id: str, next_phase: str, approvers: tuple[str, ...]) -> PhaseChangeAuditRecord:
        if len(set(approvers)) < required_approvals("phase_change"):
            raise ValueError("Phase changes require at least two unique approvers")
        state = self.get_state(election_id)
        machine = ElectionStateMachine(election_id=election_id, phase=state.phase, freeze_active=state.freeze_active)
        previous_phase = machine.phase
        machine.transition_to(next_phase)
        snapshot = ElectionControlSnapshot(
            election_id=election_id,
            phase=machine.phase,
            freeze_active=state.freeze_active,
            freeze_reason=state.freeze_reason,
        )
        self.store.save(snapshot)
        record = self.phase_auditor.record(election_id, previous_phase, machine.phase, approvers)
        self._log(
            "election_phase_changed",
            {
                "election_id": election_id,
                "previous_phase": previous_phase,
                "next_phase": machine.phase,
                "approvals": len(set(approvers)),
            },
        )
        return record

    def activate_freeze(self, election_id: str, reason: str, approvers: tuple[str, ...]) -> ElectionControlSnapshot:
        if not freeze_allowed(approvers):
            raise ValueError("Global freeze requires at least three unique approvers")
        state = self.get_state(election_id)
        snapshot = ElectionControlSnapshot(
            election_id=election_id,
            phase=state.phase,
            freeze_active=True,
            freeze_reason=reason,
        )
        self.store.save(snapshot)
        self._log(
            "control_plane_freeze_activated",
            {"election_id": election_id, "reason": reason, "approvals": len(set(approvers))},
        )
        return snapshot

    def clear_freeze(self, election_id: str, reason: str, approvers: tuple[str, ...]) -> ElectionControlSnapshot:
        if not freeze_allowed(approvers):
            raise ValueError("Freeze clearance requires at least three unique approvers")
        state = self.get_state(election_id)
        snapshot = ElectionControlSnapshot(
            election_id=election_id,
            phase=state.phase,
            freeze_active=False,
            freeze_reason=reason,
        )
        self.store.save(snapshot)
        self._log(
            "control_plane_freeze_cleared",
            {"election_id": election_id, "reason": reason, "approvals": len(set(approvers))},
        )
        return snapshot

    def phase_history(self, election_id: str) -> list[PhaseChangeAuditRecord]:
        return self.phase_auditor.history(election_id)
