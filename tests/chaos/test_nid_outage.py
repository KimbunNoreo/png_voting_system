from __future__ import annotations

import unittest

from chaos_testing.nid_outage_simulator import simulate_nid_outage


class NIDOutageChaosTests(unittest.TestCase):
    def test_outage_requires_fallback(self) -> None:
        result = simulate_nid_outage(600)
        self.assertTrue(result["fallback_required"])

    def test_outage_rejects_negative_duration(self) -> None:
        with self.assertRaises(ValueError):
            simulate_nid_outage(-1)


if __name__ == "__main__":
    unittest.main()
