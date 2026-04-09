from __future__ import annotations

import unittest

from services.voting_service.services.rate_limit_enforcer import RateLimitEnforcer


class RateLimitTests(unittest.TestCase):
    def test_per_token_limit_enforced(self) -> None:
        limiter = RateLimitEnforcer(per_token_per_minute=1, per_device_per_minute=10)
        limiter.check("token-1", "device-1")
        with self.assertRaises(ValueError):
            limiter.check("token-1", "device-1")

    def test_rate_limit_rejects_blank_identifiers(self) -> None:
        limiter = RateLimitEnforcer(per_token_per_minute=1, per_device_per_minute=10)
        with self.assertRaises(ValueError):
            limiter.check(" ", "device-1")
        with self.assertRaises(ValueError):
            limiter.check("token-1", " ")

    def test_rate_limit_rejects_invalid_configuration(self) -> None:
        with self.assertRaises(ValueError):
            RateLimitEnforcer(per_token_per_minute=0, per_device_per_minute=10)
        with self.assertRaises(ValueError):
            RateLimitEnforcer(per_token_per_minute=1, per_device_per_minute=0)
        with self.assertRaises(ValueError):
            RateLimitEnforcer(per_token_per_minute=1, per_device_per_minute=1, window_seconds=0)


if __name__ == "__main__":
    unittest.main()
