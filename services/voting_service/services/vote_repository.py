from __future__ import annotations

from contextlib import closing
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Protocol

from services.voting_service.models.vote import Vote


class VoteRepositoryStore(Protocol):
    """Persistence abstraction for encrypted vote records."""

    def save(self, vote: Vote) -> None:
        """Persist an encrypted vote."""

    def list_by_election(self, election_id: str) -> list[Vote]:
        """Return votes for an election in insertion order."""


class InMemoryVoteRepositoryStore:
    """Volatile vote repository for tests and ephemeral runtimes."""

    def __init__(self) -> None:
        self._votes: list[Vote] = []

    def save(self, vote: Vote) -> None:
        self._votes.append(vote)

    def list_by_election(self, election_id: str) -> list[Vote]:
        return [vote for vote in self._votes if vote.election_id == election_id]


class SQLiteVoteRepositoryStore:
    """Durable encrypted-vote repository backed by SQLite."""

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
                CREATE TABLE IF NOT EXISTS votes (
                    vote_id TEXT PRIMARY KEY,
                    election_id TEXT NOT NULL,
                    ballot_id TEXT NOT NULL,
                    encrypted_vote TEXT NOT NULL,
                    encrypted_key TEXT NOT NULL,
                    iv TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    device_signature TEXT NOT NULL,
                    token_hash TEXT NOT NULL,
                    kid TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_votes_election_id ON votes(election_id)")
            connection.commit()

    def save(self, vote: Vote) -> None:
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    """
                    INSERT INTO votes (
                        vote_id, election_id, ballot_id, encrypted_vote, encrypted_key,
                        iv, tag, device_id, device_signature, token_hash, kid, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        vote.vote_id,
                        vote.election_id,
                        vote.ballot_id,
                        vote.encrypted_vote,
                        vote.encrypted_key,
                        vote.iv,
                        vote.tag,
                        vote.device_id,
                        vote.device_signature,
                        vote.token_hash,
                        vote.kid,
                        vote.created_at.isoformat(),
                    ),
                )
                connection.commit()

    def list_by_election(self, election_id: str) -> list[Vote]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT vote_id, election_id, ballot_id, encrypted_vote, encrypted_key,
                       iv, tag, device_id, device_signature, token_hash, kid, created_at
                FROM votes
                WHERE election_id = ?
                ORDER BY created_at ASC
                """,
                (election_id,),
            ).fetchall()
        return [Vote.from_record(**dict(row)) for row in rows]


class VoteRepository:
    """Repository facade for encrypted vote persistence."""

    def __init__(self, store: VoteRepositoryStore | None = None) -> None:
        self.store = store or InMemoryVoteRepositoryStore()

    @classmethod
    def with_sqlite_store(cls, database_path: str) -> "VoteRepository":
        return cls(store=SQLiteVoteRepositoryStore(database_path))

    def save(self, vote: Vote) -> None:
        self.store.save(vote)

    def list_by_election(self, election_id: str) -> list[Vote]:
        return self.store.list_by_election(election_id)
