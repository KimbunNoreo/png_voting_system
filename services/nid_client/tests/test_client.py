from __future__ import annotations
import unittest
from services.nid_client.cache.token_cache import TokenCache
class TokenCacheTests(unittest.TestCase):
    def test_set_and_get(self) -> None:
        cache = TokenCache(ttl_seconds=30)
        cache.set("k", "v")
        self.assertEqual(cache.get("k"), "v")
if __name__ == "__main__":
    unittest.main()