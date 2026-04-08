from __future__ import annotations

from contextlib import closing
import json
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Protocol

from services.voting_service.models.ballot import Ballot


class BallotStore(Protocol):
    """Persistence abstraction for ballot definitions."""

    def save(self, ballot: Ballot) -> None:
        """Persist or update a ballot definition."""

    def get(self, ballot_id: str) -> Ballot | None:
        """Fetch a ballot definition by id."""


class InMemoryBallotStore:
    """Volatile ballot store for tests and ephemeral runtimes."""

    def __init__(self, ballots: list[Ballot] | None = None) -> None:
        self._ballots = {ballot.ballot_id: ballot for ballot in ballots or []}

    def save(self, ballot: Ballot) -> None:
        self._ballots[ballot.ballot_id] = ballot

    def get(self, ballot_id: str) -> Ballot | None:
        return self._ballots.get(ballot_id)


class SQLiteBallotStore:
    """Durable ballot-definition store backed by SQLite."""

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
                CREATE TABLE IF NOT EXISTS ballots (
                    ballot_id TEXT PRIMARY KEY,
                    election_id TEXT NOT NULL,
                    ballot_payload TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def save(self, ballot: Ballot) -> None:
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    """
                    INSERT INTO ballots (ballot_id, election_id, ballot_payload)
                    VALUES (?, ?, ?)
                    ON CONFLICT(ballot_id) DO UPDATE SET
                        election_id = excluded.election_id,
                        ballot_payload = excluded.ballot_payload
                    """,
                    (
                        ballot.ballot_id,
                        ballot.election_id,
                        json.dumps(ballot.to_dict(), sort_keys=True, separators=(",", ":")),
                    ),
                )
                connection.commit()

    def get(self, ballot_id: str) -> Ballot | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT ballot_payload FROM ballots WHERE ballot_id = ?",
                (ballot_id,),
            ).fetchone()
        if row is None:
            return None
        return Ballot.from_dict(json.loads(row["ballot_payload"]))


class BallotService:
    def __init__(self, ballots: list[Ballot] | None = None, store: BallotStore | None = None) -> None:
        self.store = store or InMemoryBallotStore(ballots)
        for ballot in ballots or []:
            self.store.save(ballot)

    @classmethod
    def with_sqlite_store(cls, database_path: str, ballots: list[Ballot] | None = None) -> "BallotService":
        return cls(ballots=ballots, store=SQLiteBallotStore(database_path))

    def register(self, ballot: Ballot) -> None:
        self.store.save(ballot)

    def get(self, ballot_id: str) -> Ballot:
        ballot = self.store.get(ballot_id)
        if ballot is None:
            raise ValueError("Ballot not found")
        return ballot
