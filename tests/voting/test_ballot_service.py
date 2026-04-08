from __future__ import annotations

from pathlib import Path
import unittest
from uuid import uuid4

from services.voting_service.models.ballot import Ballot, BallotContest
from services.voting_service.services.ballot_service import BallotService, SQLiteBallotStore


class BallotServiceTests(unittest.TestCase):
    def test_sqlite_ballot_service_survives_restart(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"ballots_{uuid4().hex}.sqlite3"
        ballot = Ballot(
            ballot_id="ballot-1",
            election_id="e1",
            contests=(
                BallotContest(
                    contest_id="president",
                    prompt="Select a candidate",
                    candidates=("candidate-a", "candidate-b"),
                ),
            ),
        )
        try:
            first_service = BallotService.with_sqlite_store(str(database_path), ballots=[ballot])
            self.assertEqual(first_service.get("ballot-1").election_id, "e1")

            second_service = BallotService.with_sqlite_store(str(database_path))
            loaded = second_service.get("ballot-1")
            self.assertEqual(loaded.ballot_id, ballot.ballot_id)
            self.assertEqual(loaded.contests[0].contest_id, "president")
        finally:
            if database_path.exists():
                database_path.unlink()

    def test_sqlite_ballot_store_type_is_exposed(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"ballot_store_{uuid4().hex}.sqlite3"
        try:
            service = BallotService.with_sqlite_store(str(database_path))
            self.assertIsInstance(service.store, SQLiteBallotStore)
        finally:
            if database_path.exists():
                database_path.unlink()


if __name__ == "__main__":
    unittest.main()
