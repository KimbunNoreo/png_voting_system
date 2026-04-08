from __future__ import annotations

import unittest

from services.nid_client.retry.backoff import exponential_backoff


class RetryPolicyTests(unittest.TestCase):
    def test_exponential_backoff_increases(self) -> None:
        self.assertLess(exponential_backoff(0.5, 1), exponential_backoff(0.5, 3))


if __name__ == "__main__":
    unittest.main()
