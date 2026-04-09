from __future__ import annotations

from contextlib import closing
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Protocol

from services.voting_service.models.token_replay_attempt import TokenReplayAttempt


class TokenReplayStore(Protocol):
    """Persistence abstraction for first-seen token registration."""

    def first_seen_device(self, token_hash: str) -> str | None:
        """Return the device that first registered the token hash."""

    def register_first_seen(self, token_hash: str, device_id: str) -> None:
        """Persist the first device to use the token."""

    def record_attempt(self, attempt: TokenReplayAttempt) -> None:
        """Persist a replay attempt audit entry."""


class InMemoryTokenReplayStore:
    """Development store for token replay tracking."""

    def __init__(self) -> None:
        self._first_seen_device: dict[str, str] = {}
        self._attempts: list[TokenReplayAttempt] = []

    def first_seen_device(self, token_hash: str) -> str | None:
        return self._first_seen_device.get(token_hash)

    def register_first_seen(self, token_hash: str, device_id: str) -> None:
        self._first_seen_device[token_hash] = device_id

    def record_attempt(self, attempt: TokenReplayAttempt) -> None:
        self._attempts.append(attempt)


class SQLiteTokenReplayStore:
    """Durable replay registry and audit log backed by SQLite."""

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
                CREATE TABLE IF NOT EXISTS token_first_seen (
                    token_hash TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS token_replay_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token_hash TEXT NOT NULL,
                    original_device_id TEXT NOT NULL,
                    replay_device_id TEXT NOT NULL,
                    detected_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def first_seen_device(self, token_hash: str) -> str | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT device_id FROM token_first_seen WHERE token_hash = ?",
                (token_hash,),
            ).fetchone()
        if row is None:
            return None
        return str(row["device_id"])

    def register_first_seen(self, token_hash: str, device_id: str) -> None:
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    "INSERT INTO token_first_seen (token_hash, device_id) VALUES (?, ?)",
                    (token_hash, device_id),
                )
                connection.commit()

    def record_attempt(self, attempt: TokenReplayAttempt) -> None:
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    """
                    INSERT INTO token_replay_attempts
                    (token_hash, original_device_id, replay_device_id, detected_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        attempt.token_hash,
                        attempt.original_device_id,
                        attempt.replay_device_id,
                        attempt.detected_at.isoformat(),
                    ),
                )
                connection.commit()


class TokenReplayDetector:
    """Detect global token reuse across devices and record replay attempts durably."""

    MAX_IDENTIFIER_LENGTH = 256

    def __init__(self, store: TokenReplayStore | None = None) -> None:
        self.store = store or InMemoryTokenReplayStore()

    @classmethod
    def with_sqlite_store(cls, database_path: str) -> TokenReplayDetector:
        return cls(store=SQLiteTokenReplayStore(database_path))

    def _normalize_identifier(self, value: str, *, label: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{label} is required")
        if len(normalized) > self.MAX_IDENTIFIER_LENGTH:
            raise ValueError(f"{label} is too long")
        return normalized

    def register(self, token_hash: str, device_id: str) -> TokenReplayAttempt | None:
        normalized_token_hash = self._normalize_identifier(token_hash, label="Token hash")
        normalized_device_id = self._normalize_identifier(device_id, label="Device ID")
        original = self.store.first_seen_device(normalized_token_hash)
        if original is None:
            try:
                self.store.register_first_seen(normalized_token_hash, normalized_device_id)
            except sqlite3.IntegrityError:
                original = self.store.first_seen_device(normalized_token_hash)
            else:
                return None
        if original is None or original == normalized_device_id:
            return None
        attempt = TokenReplayAttempt.create(normalized_token_hash, original, normalized_device_id)
        self.store.record_attempt(attempt)
        return attempt
