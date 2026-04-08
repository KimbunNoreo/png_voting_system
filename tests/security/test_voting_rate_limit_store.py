from __future__ import annotations

from pathlib import Path
import unittest
from uuid import uuid4

from services.voting_service.services.rate_limit_enforcer import RateLimitEnforcer, SQLiteRateLimitStore


class VotingRateLimitStoreTests(unittest.TestCase):
    def test_sqlite_rate_limit_survives_restart(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"voting_rate_limit_{uuid4().hex}.sqlite3"
        try:
            first_enforcer = RateLimitEnforcer.with_sqlite_store(
                str(database_path),
                per_token_per_minute=1,
                per_device_per_minute=10,
            )
            first_enforcer.check("token-1", "device-1")

            second_enforcer = RateLimitEnforcer.with_sqlite_store(
                str(database_path),
                per_token_per_minute=1,
                per_device_per_minute=10,
            )
            with self.assertRaises(ValueError):
                second_enforcer.check("token-1", "device-1")
        finally:
            if database_path.exists():
                database_path.unlink()

    def test_sqlite_rate_limit_store_type_is_exposed(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"voting_rate_limit_store_{uuid4().hex}.sqlite3"
        try:
            enforcer = RateLimitEnforcer.with_sqlite_store(str(database_path))
            self.assertIsInstance(enforcer.store, SQLiteRateLimitStore)
        finally:
            if database_path.exists():
                database_path.unlink()


if __name__ == "__main__":
    unittest.main()
