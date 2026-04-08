from __future__ import annotations

from pathlib import Path
import unittest
from uuid import uuid4

from services.voting_service.services.device_revocation_service import (
    DeviceRevocationService,
    SQLiteDeviceRevocationStore,
)


class DeviceRevocationStoreTests(unittest.TestCase):
    def test_sqlite_device_revocation_survives_restart(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"device_revocation_{uuid4().hex}.sqlite3"
        try:
            first_service = DeviceRevocationService.with_sqlite_store(str(database_path))
            first_service.revoke("device-1", "compromised")

            second_service = DeviceRevocationService.with_sqlite_store(str(database_path))
            with self.assertRaises(ValueError):
                second_service.assert_not_revoked("device-1")
        finally:
            if database_path.exists():
                database_path.unlink()

    def test_sqlite_device_revocation_store_type_is_exposed(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"device_revocation_store_{uuid4().hex}.sqlite3"
        try:
            service = DeviceRevocationService.with_sqlite_store(str(database_path))
            self.assertIsInstance(service.store, SQLiteDeviceRevocationStore)
        finally:
            if database_path.exists():
                database_path.unlink()


if __name__ == "__main__":
    unittest.main()
