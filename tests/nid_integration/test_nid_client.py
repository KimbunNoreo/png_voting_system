from __future__ import annotations

import unittest

from services.nid_client.client import NIDClient


class NIDClientTests(unittest.TestCase):
    def test_client_has_required_components(self) -> None:
        client = NIDClient()
        self.assertIsNotNone(client.retry_policy)
        self.assertIsNotNone(client.breaker)
        self.assertIsNotNone(client.token_cache)


if __name__ == "__main__":
    unittest.main()
