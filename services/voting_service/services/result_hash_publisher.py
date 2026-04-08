from __future__ import annotations

from contextlib import closing
import json
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Protocol

from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider
from services.voting_service.models.result_publication import ResultPublication


class ResultPublicationStore(Protocol):
    """Persistence abstraction for publicly published result hashes."""

    def save(self, publication: ResultPublication) -> None:
        """Persist a publication record."""

    def get(self, election_id: str) -> ResultPublication | None:
        """Fetch the latest published result for an election."""


class InMemoryResultPublicationStore:
    """Volatile publication store for tests and ephemeral runtimes."""

    def __init__(self) -> None:
        self._publications: dict[str, ResultPublication] = {}

    def save(self, publication: ResultPublication) -> None:
        self._publications[publication.election_id] = publication

    def get(self, election_id: str) -> ResultPublication | None:
        return self._publications.get(election_id)


class SQLiteResultPublicationStore:
    """Durable result-publication store backed by SQLite."""

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
                CREATE TABLE IF NOT EXISTS result_publications (
                    election_id TEXT PRIMARY KEY,
                    result_hash TEXT NOT NULL,
                    published_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def save(self, publication: ResultPublication) -> None:
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    """
                    INSERT INTO result_publications (election_id, result_hash, published_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(election_id) DO UPDATE SET
                        result_hash = excluded.result_hash,
                        published_at = excluded.published_at
                    """,
                    (
                        publication.election_id,
                        publication.result_hash,
                        publication.published_at.isoformat(),
                    ),
                )
                connection.commit()

    def get(self, election_id: str) -> ResultPublication | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT election_id, result_hash, published_at FROM result_publications WHERE election_id = ?",
                (election_id,),
            ).fetchone()
        if row is None:
            return None
        return ResultPublication.from_record(
            election_id=row["election_id"],
            result_hash=row["result_hash"],
            published_at=row["published_at"],
        )


class ResultHashPublisher:
    def __init__(
        self,
        crypto_provider: Phase1CryptoProvider | None = None,
        store: ResultPublicationStore | None = None,
    ) -> None:
        self.crypto_provider = crypto_provider or Phase1CryptoProvider()
        self.store = store or InMemoryResultPublicationStore()

    @classmethod
    def with_sqlite_store(cls, database_path: str) -> "ResultHashPublisher":
        return cls(store=SQLiteResultPublicationStore(database_path))

    def publish(self, election_id: str, tally: dict[str, int]) -> ResultPublication:
        canonical = json.dumps(tally, sort_keys=True, separators=(",", ":"))
        publication = ResultPublication.create(election_id=election_id, result_hash=self.crypto_provider.digest(canonical))
        self.store.save(publication)
        return publication

    def get_publication(self, election_id: str) -> ResultPublication | None:
        return self.store.get(election_id)
