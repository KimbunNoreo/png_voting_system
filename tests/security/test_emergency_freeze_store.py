from __future__ import annotations

from pathlib import Path
import unittest
from uuid import uuid4

from services.audit_service import WORMLogger
from services.voting_service.models.election_state import ElectionState
from services.voting_service.services.emergency_freeze_service import (
    EmergencyFreezeService,
    SQLiteEmergencyFreezeHistoryStore,
)


class EmergencyFreezeStoreTests(unittest.TestCase):
    def test_sqlite_emergency_freeze_history_survives_restart(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"emergency_freeze_{uuid4().hex}.sqlite3"
        try:
            first_service = EmergencyFreezeService.with_sqlite_store(
                str(database_path),
                audit_logger=WORMLogger(),
            )
            state = ElectionState(election_id="e1", phase="voting", freeze_active=False)
            first_service.activate(state, "incident", 3)

            second_service = EmergencyFreezeService.with_sqlite_store(str(database_path))
            history = second_service.history_store.history("e1")
            self.assertEqual(len(history), 1)
            self.assertTrue(history[0].activated)
        finally:
            if database_path.exists():
                database_path.unlink()

    def test_sqlite_emergency_freeze_store_type_is_exposed(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"emergency_freeze_store_{uuid4().hex}.sqlite3"
        try:
            service = EmergencyFreezeService.with_sqlite_store(str(database_path))
            self.assertIsInstance(service.history_store, SQLiteEmergencyFreezeHistoryStore)
        finally:
            if database_path.exists():
                database_path.unlink()


if __name__ == "__main__":
    unittest.main()
