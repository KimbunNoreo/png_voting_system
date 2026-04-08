from __future__ import annotations

from pathlib import Path
import unittest
from uuid import uuid4

from services.voting_service.services.result_hash_publisher import ResultHashPublisher, SQLiteResultPublicationStore


class ResultHashPublisherTests(unittest.TestCase):
    def test_sqlite_publisher_survives_restart(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"result_publications_{uuid4().hex}.sqlite3"
        try:
            first_publisher = ResultHashPublisher.with_sqlite_store(str(database_path))
            publication = first_publisher.publish("e1", {"candidate-a": 5, "candidate-b": 3})

            second_publisher = ResultHashPublisher.with_sqlite_store(str(database_path))
            loaded = second_publisher.get_publication("e1")
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded.election_id, publication.election_id)
            self.assertEqual(loaded.result_hash, publication.result_hash)
        finally:
            if database_path.exists():
                database_path.unlink()

    def test_sqlite_store_type_is_exposed(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"result_store_{uuid4().hex}.sqlite3"
        try:
            publisher = ResultHashPublisher.with_sqlite_store(str(database_path))
            self.assertIsInstance(publisher.store, SQLiteResultPublicationStore)
        finally:
            if database_path.exists():
                database_path.unlink()


if __name__ == "__main__":
    unittest.main()
