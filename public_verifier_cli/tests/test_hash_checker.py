from __future__ import annotations

import unittest

from public_verifier_cli.hash_checker import verify_result_hash
from public_verification.result_hash_publisher import publish_result_hash


class HashCheckerTests(unittest.TestCase):
    def test_hash_checker_accepts_matching_hash(self) -> None:
        tally = {"candidate-a": 7}
        publication = publish_result_hash("e1", tally)
        self.assertTrue(verify_result_hash("e1", tally, publication.result_hash))


if __name__ == "__main__":
    unittest.main()
