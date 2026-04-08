from __future__ import annotations

from pathlib import Path
import unittest
from uuid import uuid4

from services.audit_service.detection.tamper import verify_hash_chain
from services.audit_service.logger.worm_logger import SQLiteAuditStore, WORMLogger


class AuditWORMLoggerTests(unittest.TestCase):
    def test_sqlite_worm_logger_survives_restart(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"audit_log_{uuid4().hex}.sqlite3"
        try:
            first_logger = WORMLogger.with_sqlite_store(str(database_path))
            first_logger.append("vote_cast", {"vote_id": "vote-1", "election_id": "e1"})

            second_logger = WORMLogger.with_sqlite_store(str(database_path))
            second_logger.append("results_published", {"election_id": "e1"})

            entries = second_logger.entries()
            self.assertEqual(len(entries), 2)
            self.assertEqual(entries[0].event_type, "vote_cast")
            self.assertEqual(entries[1].event_type, "results_published")
            self.assertTrue(verify_hash_chain(entries))
        finally:
            if database_path.exists():
                database_path.unlink()

    def test_sqlite_store_type_is_exposed_for_factory_assertions(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"audit_store_{uuid4().hex}.sqlite3"
        try:
            logger = WORMLogger.with_sqlite_store(str(database_path))
            self.assertIsInstance(logger.store, SQLiteAuditStore)
        finally:
            if database_path.exists():
                database_path.unlink()

    def test_logger_redacts_sensitive_payload_fields(self) -> None:
        logger = WORMLogger()
        entry = logger.append(
            "identity_boundary_test",
            {
                "election_id": "e1",
                "token_hash": "safe-hash",
                "token": "raw-token-should-never-appear",
                "sub": "citizen-123",
                "name": "Sensitive Name",
                "nested": {
                    "address": "Sensitive Address",
                    "biometrics": {"face": "template"},
                },
            },
        )
        self.assertEqual(entry.payload["election_id"], "e1")
        self.assertEqual(entry.payload["token_hash"], "safe-hash")
        self.assertEqual(entry.payload["token"], "[redacted]")
        self.assertEqual(entry.payload["sub"], "[redacted]")
        self.assertEqual(entry.payload["name"], "[redacted]")
        self.assertEqual(entry.payload["nested"]["address"], "[redacted]")
        self.assertEqual(entry.payload["nested"]["biometrics"], "[redacted]")


if __name__ == "__main__":
    unittest.main()
