from __future__ import annotations

from pathlib import Path
import unittest
from uuid import uuid4

from services.voting_service.models.election_state import ElectionState
from services.voting_service.services.election_state_manager import ElectionStateManager, SQLiteElectionStateStore


class ElectionStateManagerStoreTests(unittest.TestCase):
    def test_sqlite_election_state_survives_restart(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"election_state_{uuid4().hex}.sqlite3"
        try:
            first_manager = ElectionStateManager.with_sqlite_store(
                str(database_path),
                initial_state=ElectionState("e1", "registration", False),
            )
            first_manager.transition("verification")
            first_manager.transition("voting")

            second_manager = ElectionStateManager.with_sqlite_store(
                str(database_path),
                initial_state=ElectionState("e1", "registration", False),
            )
            self.assertEqual(second_manager.state.phase, "voting")
        finally:
            if database_path.exists():
                database_path.unlink()

    def test_sqlite_election_state_store_type_is_exposed(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"election_state_store_{uuid4().hex}.sqlite3"
        try:
            manager = ElectionStateManager.with_sqlite_store(
                str(database_path),
                initial_state=ElectionState("e1", "voting", False),
            )
            self.assertIsInstance(manager.store, SQLiteElectionStateStore)
        finally:
            if database_path.exists():
                database_path.unlink()


if __name__ == "__main__":
    unittest.main()
