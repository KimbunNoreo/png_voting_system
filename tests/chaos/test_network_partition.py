from __future__ import annotations

import unittest

from chaos_testing.network_partition_test import simulate_network_partition


class NetworkPartitionChaosTests(unittest.TestCase):
    def test_partition_marks_system_degraded(self) -> None:
        result = simulate_network_partition(False)
        self.assertTrue(result["degraded"])


if __name__ == "__main__":
    unittest.main()
