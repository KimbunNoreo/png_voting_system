from __future__ import annotations
import unittest
from services.nid_client.client import NIDClient
class NIDClientConstructionTests(unittest.TestCase):
    def test_client_constructs(self) -> None:
        client = NIDClient()
        self.assertIsNotNone(client.retry_policy)
        self.assertIsNotNone(client.breaker)
if __name__ == "__main__":
    unittest.main()