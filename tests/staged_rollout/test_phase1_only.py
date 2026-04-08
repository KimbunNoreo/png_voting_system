from __future__ import annotations

import unittest

from config import get_settings
from scripts.staged_rollout_switch import enforce_phase1_only


class Phase1OnlyTests(unittest.TestCase):
    def test_phase1_flag_is_enforced(self) -> None:
        settings = get_settings()
        self.assertTrue(settings.staged_rollout.phase1_only)
        self.assertEqual(enforce_phase1_only("phase1"), "phase1")
        with self.assertRaises(ValueError):
            enforce_phase1_only("phase2")


if __name__ == "__main__":
    unittest.main()
