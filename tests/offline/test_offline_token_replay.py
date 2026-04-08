from __future__ import annotations

import unittest

from services.offline_sync_service.sync.conflict_resolution import resolve_conflicts, resolve_conflicts_with_report


class OfflineTokenReplayTests(unittest.TestCase):
    def test_conflict_resolution_keeps_earliest_token_use(self) -> None:
        merged = resolve_conflicts(
            [{"token_hash": "t1", "created_at": "2026-04-06T00:00:00Z"}],
            [{"token_hash": "t1", "created_at": "2026-04-06T00:01:00Z"}],
        )
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["created_at"], "2026-04-06T00:00:00Z")

    def test_conflict_resolution_redacts_sensitive_fields(self) -> None:
        merged = resolve_conflicts(
            [{"token_hash": "t2", "created_at": "2026-04-06T00:00:00Z", "sub": "citizen-1"}],
            [{"token_hash": "t2", "created_at": "2026-04-06T00:01:00Z", "biometrics": {"face": "template"}}],
        )
        self.assertEqual(merged[0]["sub"], "[redacted]")

    def test_conflict_report_captures_winner_and_discarded_timestamps(self) -> None:
        _, report = resolve_conflicts_with_report(
            [{"token_hash": "t3", "created_at": "2026-04-06T00:00:00Z"}],
            [{"token_hash": "t3", "created_at": "2026-04-06T00:01:00Z"}],
        )
        self.assertEqual(report.conflict_count, 1)
        self.assertEqual(report.decisions[0].winner_created_at, "2026-04-06T00:00:00Z")
        self.assertEqual(report.decisions[0].discarded_created_at, "2026-04-06T00:01:00Z")


if __name__ == "__main__":
    unittest.main()
