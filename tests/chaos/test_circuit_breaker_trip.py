from __future__ import annotations

import unittest

from chaos_testing.chaos_reporter import build_report
from chaos_testing.nid_outage_simulator import simulate_nid_outage


class CircuitBreakerTripChaosTests(unittest.TestCase):
    def test_report_contains_degraded_scenarios(self) -> None:
        report = build_report([simulate_nid_outage(30)])
        self.assertIn("nid_outage", report["degraded_scenarios"])


if __name__ == "__main__":
    unittest.main()
