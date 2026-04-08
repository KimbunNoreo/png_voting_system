from __future__ import annotations

import unittest

from services.voting_service.models.vote import Vote


class SecretBallotComplianceTests(unittest.TestCase):
    def test_vote_model_contains_token_hash_but_no_identity_fields(self) -> None:
        field_names = set(Vote.__dataclass_fields__)
        self.assertIn("token_hash", field_names)
        self.assertNotIn("name", field_names)
        self.assertNotIn("citizen_reference", field_names)
        self.assertNotIn("address", field_names)


if __name__ == "__main__":
    unittest.main()
