from __future__ import annotations

import unittest

from scripts.emergency_break_glass import activate_break_glass


class BreakGlassScriptTests(unittest.TestCase):
    def test_break_glass_requires_multiple_approvers(self) -> None:
        with self.assertRaises(ValueError):
            activate_break_glass(("official-1",), "emergency")
        result = activate_break_glass(("official-1", "official-2"), "emergency")
        self.assertEqual(result["status"], "approved")


if __name__ == "__main__":
    unittest.main()
