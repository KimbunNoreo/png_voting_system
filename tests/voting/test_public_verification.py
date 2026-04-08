from __future__ import annotations

import unittest

from public_verification.public_api import get_public_result
from public_verification.result_disclosure import disclose_results
from public_verification.result_hash_publisher import publish_result_hash


class PublicVerificationTests(unittest.TestCase):
    def test_public_result_and_disclosure_verify(self) -> None:
        tally = {"candidate-a": 10, "candidate-b": 4}
        publication = publish_result_hash("e1", tally)
        public_payload = get_public_result(publication)
        disclosed = disclose_results(publication, tally)
        self.assertEqual(public_payload["election_id"], "e1")
        self.assertTrue(disclosed["verified"])

    def test_disclosure_normalizes_tally_to_deterministic_ints(self) -> None:
        publication = publish_result_hash("e1", {"candidate-b": 4, "candidate-a": 10})
        disclosed = disclose_results(publication, {"candidate-a": "10", "candidate-b": 4})
        self.assertEqual(
            disclosed["tally"],
            {"candidate-a": 10, "candidate-b": 4},
        )
        self.assertTrue(disclosed["verified"])


if __name__ == "__main__":
    unittest.main()
