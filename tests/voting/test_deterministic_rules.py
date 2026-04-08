from __future__ import annotations

import unittest

from services.voting_service.anti_fraud.deterministic_rules import evaluate_rules


class DeterministicRulesTests(unittest.TestCase):
    def test_rules_block_replay(self) -> None:
        decision = evaluate_rules(replay_detected=True, device_revoked=False, within_time_window=True)
        self.assertFalse(decision.allowed)
        self.assertIn("token_replay_detected", decision.reasons)


if __name__ == "__main__":
    unittest.main()
