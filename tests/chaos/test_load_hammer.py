from __future__ import annotations

import unittest

from chaos_testing.load_hammer import simulate_load


class LoadHammerChaosTests(unittest.TestCase):
    def test_load_hammer_flags_limit_exceeded(self) -> None:
        result = simulate_load(200, 100)
        self.assertTrue(result["limit_exceeded"])

    def test_load_hammer_rejects_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            simulate_load(-1, 100)
        with self.assertRaises(ValueError):
            simulate_load(10, 0)


if __name__ == "__main__":
    unittest.main()
