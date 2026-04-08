from __future__ import annotations

from contextlib import closing
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Protocol

from services.voting_service.models.used_token import UsedToken


class UsedTokenStore(Protocol):
    """Persistence abstraction for consumed token records."""

    def get(self, token_hash: str) -> UsedToken | None:
        """Return the consumed token entry when one exists."""

    def put(self, token: UsedToken) -> None:
        """Persist a newly consumed token."""


class InMemoryUsedTokenStore:
    """Development store for consumed token tracking."""

    def __init__(self) -> None:
        self._tokens: dict[str, UsedToken] = {}

    def get(self, token_hash: str) -> UsedToken | None:
        return self._tokens.get(token_hash)

    def put(self, token: UsedToken) -> None:
        self._tokens[token.token_hash] = token


class SQLiteUsedTokenStore:
    """Durable consumed-token registry backed by SQLite."""

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
                CREATE TABLE IF NOT EXISTS used_tokens (
                    token_hash TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    consumed_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def get(self, token_hash: str) -> UsedToken | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT token_hash, device_id, consumed_at FROM used_tokens WHERE token_hash = ?",
                (token_hash,),
            ).fetchone()
        if row is None:
            return None
        return UsedToken.from_record(
            token_hash=row["token_hash"],
            device_id=row["device_id"],
            consumed_at=row["consumed_at"],
        )

    def put(self, token: UsedToken) -> None:
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    "INSERT INTO used_tokens (token_hash, device_id, consumed_at) VALUES (?, ?, ?)",
                    (token.token_hash, token.device_id, token.consumed_at.isoformat()),
                )
                connection.commit()


class TokenConsumer:
    """One-time-use token registry enforcing durable token consumption."""

    def __init__(self, store: UsedTokenStore | None = None) -> None:
        self.store = store or InMemoryUsedTokenStore()

    @classmethod
    def with_sqlite_store(cls, database_path: str) -> TokenConsumer:
        return cls(store=SQLiteUsedTokenStore(database_path))

    def consume(self, token_hash: str, device_id: str) -> UsedToken:
        if self.store.get(token_hash) is not None:
            raise ValueError("Token has already been consumed")
        token = UsedToken.create(token_hash, device_id)
        try:
            self.store.put(token)
        except sqlite3.IntegrityError as exc:
            raise ValueError("Token has already been consumed") from exc
        return token

    def is_consumed(self, token_hash: str) -> bool:
        return self.store.get(token_hash) is not None
