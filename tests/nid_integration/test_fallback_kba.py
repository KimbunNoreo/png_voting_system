from __future__ import annotations

import unittest

from services.nid_client.circuit_breaker.fallback import KBAMultiPersonFallback
from services.nid_client.exceptions import NIDUnavailableError


class FallbackKBATests(unittest.TestCase):
    def test_fallback_blocks_and_requires_approvals(self) -> None:
        with self.assertRaises(NIDUnavailableError):
            KBAMultiPersonFallback(required_approvals=2).block("nid offline")


if __name__ == "__main__":
    unittest.main()
