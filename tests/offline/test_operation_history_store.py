from __future__ import annotations

from pathlib import Path
import unittest

from services.offline_sync_service.operation_history import OfflineSyncOperationHistory


class OfflineSyncOperationHistoryStoreTests(unittest.TestCase):
    def test_sqlite_operation_history_survives_restart(self) -> None:
        runtime_dir = Path("data/test_runtime")
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / "offline_sync_operations_test.sqlite3"
        if database_path.exists():
            database_path.unlink()
        history = OfflineSyncOperationHistory.with_sqlite_store(str(database_path))
        history.append(
            operation_id="operation-1",
            operator_id="operator-1",
            device_id="device-1",
            manifest_digest="sha256:abc",
            manifest_signature="signature-1",
            record_count=3,
            conflict_count=1,
            manifest_valid=True,
            approvals=("official-1", "official-2"),
            conflict_report={"conflict_count": 1, "decisions": []},
        )

        reopened = OfflineSyncOperationHistory.with_sqlite_store(str(database_path))
        records = reopened.history()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].operation_id, "operation-1")
        self.assertEqual(records[0].approvals, ("official-1", "official-2"))
        self.assertTrue(records[0].manifest_valid)
        if database_path.exists():
            database_path.unlink()


if __name__ == "__main__":
    unittest.main()
