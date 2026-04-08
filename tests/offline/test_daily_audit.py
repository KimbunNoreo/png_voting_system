from __future__ import annotations

import unittest

from services.voting_service.models.vote import Vote
from services.voting_service.services.daily_audit import DailyAuditService


class OfflineDailyAuditTests(unittest.TestCase):
    def test_daily_audit_produces_digest(self) -> None:
        vote = Vote.create(
            vote_id="v1",
            election_id="e1",
            ballot_id="b1",
            encrypted_vote="cipher",
            encrypted_key="wrapped",
            iv="iv",
            tag="tag",
            device_id="device-1",
            device_signature="sig",
            token_hash="hash",
            kid="phase1-default",
        )
        audit = DailyAuditService().build("device-1", "2026-04-06", [vote])
        self.assertEqual(audit.device_id, "device-1")
        self.assertTrue(audit.digest)


if __name__ == "__main__":
    unittest.main()
