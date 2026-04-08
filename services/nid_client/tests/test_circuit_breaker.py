from __future__ import annotations
import unittest
from services.nid_client.circuit_breaker.breaker import CircuitBreaker
from services.nid_client.exceptions import NIDUnavailableError
class CircuitBreakerTests(unittest.TestCase):
    def test_breaker_opens_after_threshold(self) -> None:
        breaker = CircuitBreaker(failure_threshold=2, reset_timeout_seconds=60)
        breaker.record_failure(); breaker.record_failure()
        with self.assertRaises(NIDUnavailableError):
            breaker.before_request()
if __name__ == "__main__":
    unittest.main()