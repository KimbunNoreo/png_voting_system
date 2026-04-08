from __future__ import annotations

import unittest

from public_verification.public_api import get_public_result
from public_verification.result_hash_publisher import publish_result_hash


class AccessibilityComplianceTests(unittest.TestCase):
    def test_public_result_payload_is_plain_readable_structure(self) -> None:
        publication = publish_result_hash("e1", {"candidate-a": 1})
        payload = get_public_result(publication)
        self.assertIn("election_id", payload)
        self.assertIn("result_hash", payload)
        self.assertIn("published_at", payload)


if __name__ == "__main__":
    unittest.main()
