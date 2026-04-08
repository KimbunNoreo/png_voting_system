from __future__ import annotations

from pathlib import Path
import unittest
from uuid import uuid4

from services.voting_service.anti_fraud.duplicate import is_duplicate
from services.voting_service.services.token_consumer import TokenConsumer


class DuplicateDetectionTests(unittest.TestCase):
    def test_duplicate_detected_after_consumption(self) -> None:
        consumer = TokenConsumer()
        token_hash = "abc"
        self.assertFalse(is_duplicate(token_hash, consumer))
        consumer.consume(token_hash, "device-1")
        self.assertTrue(is_duplicate(token_hash, consumer))

    def test_duplicate_detection_survives_consumer_restart_with_sqlite_store(self) -> None:
        database_dir = Path("data") / "test_runtime"
        database_dir.mkdir(parents=True, exist_ok=True)
        database_path = database_dir / f"used_tokens_{uuid4().hex}.sqlite3"
        try:
            first_consumer = TokenConsumer.with_sqlite_store(database_path)
            token_hash = "durable-token"
            first_consumer.consume(token_hash, "device-1")

            second_consumer = TokenConsumer.with_sqlite_store(database_path)
            self.assertTrue(is_duplicate(token_hash, second_consumer))
            with self.assertRaises(ValueError):
                second_consumer.consume(token_hash, "device-2")
        finally:
            if database_path.exists():
                database_path.unlink()


if __name__ == "__main__":
    unittest.main()
