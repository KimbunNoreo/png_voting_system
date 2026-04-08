from __future__ import annotations

from contextlib import closing
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Protocol

from services.voting_service.models.device_revocation import DeviceRevocation


class DeviceRevocationStore(Protocol):
    """Persistence abstraction for revoked devices."""

    def save(self, revocation: DeviceRevocation) -> None:
        """Persist a device revocation entry."""

    def get(self, device_id: str) -> DeviceRevocation | None:
        """Fetch a device revocation entry when one exists."""


class InMemoryDeviceRevocationStore:
    """Volatile revocation store for tests and ephemeral runtimes."""

    def __init__(self) -> None:
        self._revoked: dict[str, DeviceRevocation] = {}

    def save(self, revocation: DeviceRevocation) -> None:
        self._revoked[revocation.device_id] = revocation

    def get(self, device_id: str) -> DeviceRevocation | None:
        return self._revoked.get(device_id)


class SQLiteDeviceRevocationStore:
    """Durable device-revocation store backed by SQLite."""

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
                CREATE TABLE IF NOT EXISTS device_revocations (
                    device_id TEXT PRIMARY KEY,
                    reason TEXT NOT NULL,
                    revoked_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def save(self, revocation: DeviceRevocation) -> None:
        with self._lock:
            with closing(self._connect()) as connection:
                connection.execute(
                    """
                    INSERT INTO device_revocations (device_id, reason, revoked_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(device_id) DO UPDATE SET
                        reason = excluded.reason,
                        revoked_at = excluded.revoked_at
                    """,
                    (revocation.device_id, revocation.reason, revocation.revoked_at.isoformat()),
                )
                connection.commit()

    def get(self, device_id: str) -> DeviceRevocation | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT device_id, reason, revoked_at FROM device_revocations WHERE device_id = ?",
                (device_id,),
            ).fetchone()
        if row is None:
            return None
        return DeviceRevocation.from_record(
            device_id=row["device_id"],
            reason=row["reason"],
            revoked_at=row["revoked_at"],
        )


class DeviceRevocationService:
    def __init__(self, store: DeviceRevocationStore | None = None) -> None:
        self.store = store or InMemoryDeviceRevocationStore()

    @classmethod
    def with_sqlite_store(cls, database_path: str) -> "DeviceRevocationService":
        return cls(store=SQLiteDeviceRevocationStore(database_path))

    def revoke(self, device_id: str, reason: str) -> DeviceRevocation:
        revocation = DeviceRevocation.create(device_id, reason)
        self.store.save(revocation)
        return revocation

    def assert_not_revoked(self, device_id: str) -> None:
        if self.store.get(device_id) is not None:
            raise ValueError("Device has been revoked")
