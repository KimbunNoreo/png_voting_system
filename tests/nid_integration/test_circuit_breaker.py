from __future__ import annotations

import unittest

from services.nid_client.circuit_breaker.breaker import CircuitBreaker
from services.nid_client.exceptions import NIDUnavailableError


class NIDCircuitBreakerTests(unittest.TestCase):
    def test_open_breaker_blocks_request(self) -> None:
        breaker = CircuitBreaker(failure_threshold=1, reset_timeout_seconds=60)
        breaker.record_failure()
        with self.assertRaises(NIDUnavailableError):
            breaker.before_request()


if __name__ == "__main__":
    unittest.main()
