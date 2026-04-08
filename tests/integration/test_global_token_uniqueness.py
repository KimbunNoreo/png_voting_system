from __future__ import annotations

import unittest

from services.voting_service.services.token_replay_detector import TokenReplayDetector


class GlobalTokenUniquenessTests(unittest.TestCase):
    def test_only_one_device_can_claim_token_hash(self) -> None:
        detector = TokenReplayDetector()
        detector.register("token-1", "device-a")
        replay = detector.register("token-1", "device-b")
        self.assertIsNotNone(replay)


if __name__ == "__main__":
    unittest.main()
