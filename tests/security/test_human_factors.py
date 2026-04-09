from __future__ import annotations

import unittest

from human_factors.multi_person_auth.freeze_authorization import freeze_allowed
from human_factors.multi_person_auth.session_requirements import required_approvals
from human_factors.observer_program.observer_verification import observer_verified


class HumanFactorsTests(unittest.TestCase):
    def test_freeze_authorization_threshold(self) -> None:
        self.assertFalse(freeze_allowed(("a", "b")))
        self.assertTrue(freeze_allowed(("a", "b", "c")))
        self.assertTrue(freeze_allowed(("a", "b", "c", "d", "e")))
        self.assertFalse(freeze_allowed(("a", "b", "c", "d", "e", "f")))
        self.assertTrue(freeze_allowed(("a", "b", "c", "a")))

    def test_required_approvals_for_operations(self) -> None:
        self.assertEqual(required_approvals("global_freeze"), 3)
        self.assertEqual(required_approvals("break_glass"), 2)

    def test_observer_key_validation(self) -> None:
        self.assertTrue(observer_verified("observer-abc-readonly"))
        self.assertFalse(observer_verified("admin-token"))


if __name__ == "__main__":
    unittest.main()
