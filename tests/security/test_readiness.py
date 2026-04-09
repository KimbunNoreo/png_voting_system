from __future__ import annotations

import unittest

from services.readiness import READINESS_PROFILES, run_readiness_suite


class ReadinessTests(unittest.TestCase):
    def test_profiles_include_quick_and_core(self) -> None:
        self.assertIn("quick", READINESS_PROFILES)
        self.assertIn("core", READINESS_PROFILES)
        self.assertTrue(READINESS_PROFILES["quick"])
        self.assertTrue(READINESS_PROFILES["core"])

    def test_unknown_profile_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_readiness_suite("unknown-profile", verbosity=0)


if __name__ == "__main__":
    unittest.main()
