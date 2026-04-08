from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import unittest
from uuid import uuid4

from services.voting_service.models.vote import Vote
from services.voting_service.services.vote_repository import SQLiteVoteRepositoryStore, VoteRepository


class VoteRepositoryTests(unittest.TestCase):
    def test_sqlite_vote_repository_survives_restart(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"votes_{uuid4().hex}.sqlite3"
        vote = Vote(
            vote_id="vote-1",
            election_id="e1",
            ballot_id="ballot-1",
            encrypted_vote="ciphertext",
            encrypted_key="encrypted-key",
            iv="iv",
            tag="tag",
            device_id="device-1",
            device_signature="signature",
            token_hash="token-hash",
            kid="phase1-default",
            created_at=datetime.now(timezone.utc),
        )
        try:
            first_repo = VoteRepository.with_sqlite_store(str(database_path))
            first_repo.save(vote)

            second_repo = VoteRepository.with_sqlite_store(str(database_path))
            votes = second_repo.list_by_election("e1")
            self.assertEqual(len(votes), 1)
            self.assertEqual(votes[0].vote_id, "vote-1")
        finally:
            if database_path.exists():
                database_path.unlink()

    def test_sqlite_vote_repository_store_type_is_exposed(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"vote_store_{uuid4().hex}.sqlite3"
        try:
            repository = VoteRepository.with_sqlite_store(str(database_path))
            self.assertIsInstance(repository.store, SQLiteVoteRepositoryStore)
        finally:
            if database_path.exists():
                database_path.unlink()


if __name__ == "__main__":
    unittest.main()
