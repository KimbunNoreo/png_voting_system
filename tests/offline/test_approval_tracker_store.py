from __future__ import annotations

from pathlib import Path
import unittest
from uuid import uuid4

from human_factors.multi_person_auth.approval_tracking import ApprovalTracker, SQLiteApprovalStore


class ApprovalTrackerStoreTests(unittest.TestCase):
    def test_sqlite_approval_tracker_survives_restart(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"offline_approvals_{uuid4().hex}.sqlite3"
        try:
            first = ApprovalTracker.with_sqlite_store(str(database_path))
            self.assertEqual(first.approve("op-1", "official-1"), 1)
            self.assertEqual(first.approve("op-1", "official-2"), 2)

            second = ApprovalTracker.with_sqlite_store(str(database_path))
            history = second.history("op-1")
            self.assertEqual(len(history), 2)
            self.assertEqual(history[0].approver, "official-1")
            self.assertEqual(history[1].approval_count, 2)
        finally:
            if database_path.exists():
                database_path.unlink()

    def test_sqlite_store_type_is_exposed(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"offline_approvals_store_{uuid4().hex}.sqlite3"
        try:
            tracker = ApprovalTracker.with_sqlite_store(str(database_path))
            self.assertIsInstance(tracker.store, SQLiteApprovalStore)
        finally:
            if database_path.exists():
                database_path.unlink()


if __name__ == "__main__":
    unittest.main()
