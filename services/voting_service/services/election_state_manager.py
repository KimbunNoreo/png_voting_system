from __future__ import annotations

from contextlib import closing
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Protocol

from services.voting_service.models.election_state import ElectionState


class ElectionStateStore(Protocol):
    """Persistence abstraction for election phase state."""

    def save(self, state: ElectionState) -> None:
        """Persist the current state."""

    def load(self, election_id: str) -> ElectionState | None:
        """Load the state for an election."""


class InMemoryElectionStateStore:
    """Volatile election-state store for tests and ephemeral runtimes."""

    def __init__(self) -> None:
        self._states: dict[str, ElectionState] = {}

    def save(self, state: ElectionState) -> None:
        self._states[state.election_id] = state

    def load(self, election_id: str) -> ElectionState | None:
        return self._states.get(election_id)


class SQLiteElectionStateStore:
    """Durable election-state store backed by SQLite."""

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
                CREATE TABLE IF NOT EXISTS election_states (
                    election_id TEXT PRIMARY KEY,
                    phase TEXT NOT NULL,
                    freeze_active INTEGER NOT NULL
                )
                """
            )
            connection.commit()

    def save(self, state: ElectionState) -> None:
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    """
                    INSERT INTO election_states (election_id, phase, freeze_active)
                    VALUES (?, ?, ?)
                    ON CONFLICT(election_id) DO UPDATE SET
                        phase = excluded.phase,
                        freeze_active = excluded.freeze_active
                    """,
                    (state.election_id, state.phase, int(state.freeze_active)),
                )
                connection.commit()

    def load(self, election_id: str) -> ElectionState | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT election_id, phase, freeze_active FROM election_states WHERE election_id = ?",
                (election_id,),
            ).fetchone()
        if row is None:
            return None
        return ElectionState.from_record(
            election_id=row["election_id"],
            phase=row["phase"],
            freeze_active=row["freeze_active"],
        )


class ElectionStateManager:
    VALID_PHASES = ("registration", "verification", "voting", "locked", "counting", "finalized")

    def __init__(self, initial_state: ElectionState, store: ElectionStateStore | None = None) -> None:
        self.store = store or InMemoryElectionStateStore()
        self.store.save(initial_state)
        self.state = self.store.load(initial_state.election_id) or initial_state

    @classmethod
    def with_sqlite_store(cls, database_path: str, initial_state: ElectionState) -> "ElectionStateManager":
        store = SQLiteElectionStateStore(database_path)
        existing_state = store.load(initial_state.election_id)
        return cls(existing_state or initial_state, store=store)

    def set_state(self, state: ElectionState) -> ElectionState:
        self.store.save(state)
        self.state = state
        return state

    def ensure_voting_open(self) -> None:
        self.state = self.store.load(self.state.election_id) or self.state
        if self.state.freeze_active: raise ValueError("Election is frozen")
        if self.state.phase != "voting": raise ValueError(f"Voting is not allowed during {self.state.phase}")

    def transition(self, next_phase: str) -> ElectionState:
        if next_phase not in self.VALID_PHASES: raise ValueError("Invalid election phase")
        return self.set_state(
            ElectionState(election_id=self.state.election_id, phase=next_phase, freeze_active=self.state.freeze_active)
        )
