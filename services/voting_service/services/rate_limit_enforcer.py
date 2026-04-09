from __future__ import annotations

from collections import defaultdict, deque
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Protocol


class RateLimitStore(Protocol):
    """Persistence abstraction for token and device sliding windows."""

    def add_and_count(self, scope: str, identifier: str, now: datetime, window_seconds: int) -> int:
        """Persist a request hit and return the active count inside the window."""


class InMemoryRateLimitStore:
    """Volatile rate-limit store for tests and ephemeral runtimes."""

    def __init__(self) -> None:
        self._windows: dict[tuple[str, str], deque[datetime]] = defaultdict(deque)

    def add_and_count(self, scope: str, identifier: str, now: datetime, window_seconds: int) -> int:
        window = self._windows[(scope, identifier)]
        cutoff = now - timedelta(seconds=window_seconds)
        while window and window[0] <= cutoff:
            window.popleft()
        window.append(now)
        return len(window)


class SQLiteRateLimitStore:
    """Durable rate-limit store backed by SQLite."""

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
                CREATE TABLE IF NOT EXISTS rate_limit_hits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scope TEXT NOT NULL,
                    identifier TEXT NOT NULL,
                    hit_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_rate_limit_scope_identifier ON rate_limit_hits(scope, identifier)"
            )
            connection.commit()

    def add_and_count(self, scope: str, identifier: str, now: datetime, window_seconds: int) -> int:
        cutoff = now - timedelta(seconds=window_seconds)
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    "DELETE FROM rate_limit_hits WHERE scope = ? AND identifier = ? AND hit_at <= ?",
                    (scope, identifier, cutoff.isoformat()),
                )
                connection.execute(
                    "INSERT INTO rate_limit_hits (scope, identifier, hit_at) VALUES (?, ?, ?)",
                    (scope, identifier, now.isoformat()),
                )
                row = connection.execute(
                    "SELECT COUNT(*) AS count FROM rate_limit_hits WHERE scope = ? AND identifier = ?",
                    (scope, identifier),
                ).fetchone()
                connection.commit()
        return int(row["count"])


class RateLimitEnforcer:
    MAX_IDENTIFIER_LENGTH = 256

    def __init__(
        self,
        per_token_per_minute: int = 1,
        per_device_per_minute: int = 10,
        *,
        store: RateLimitStore | None = None,
        window_seconds: int = 60,
    ) -> None:
        if per_token_per_minute <= 0:
            raise ValueError("Per-token rate limit must be positive")
        if per_device_per_minute <= 0:
            raise ValueError("Per-device rate limit must be positive")
        if window_seconds <= 0:
            raise ValueError("Rate limit window must be positive")
        self.per_token = per_token_per_minute
        self.per_device = per_device_per_minute
        self.window_seconds = window_seconds
        self.store = store or InMemoryRateLimitStore()

    @classmethod
    def with_sqlite_store(
        cls,
        database_path: str,
        *,
        per_token_per_minute: int = 1,
        per_device_per_minute: int = 10,
        window_seconds: int = 60,
    ) -> "RateLimitEnforcer":
        return cls(
            per_token_per_minute=per_token_per_minute,
            per_device_per_minute=per_device_per_minute,
            store=SQLiteRateLimitStore(database_path),
            window_seconds=window_seconds,
        )

    def _normalize_identifier(self, value: str, *, label: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{label} is required")
        if len(normalized) > self.MAX_IDENTIFIER_LENGTH:
            raise ValueError(f"{label} is too long")
        return normalized

    def check(self, token_hash: str, device_id: str) -> None:
        normalized_token_hash = self._normalize_identifier(token_hash, label="Token hash")
        normalized_device_id = self._normalize_identifier(device_id, label="Device ID")
        now = datetime.now(timezone.utc)
        token_count = self.store.add_and_count("token", normalized_token_hash, now, self.window_seconds)
        if token_count > self.per_token:
            raise ValueError("Per-token rate limit exceeded")
        device_count = self.store.add_and_count("device", normalized_device_id, now, self.window_seconds)
        if device_count > self.per_device:
            raise ValueError("Per-device rate limit exceeded")
