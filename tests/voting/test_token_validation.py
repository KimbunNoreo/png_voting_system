from __future__ import annotations

import unittest

from services.voting_service.services.verification_gateway import VerificationGateway


class StubClient:
    def validate_token(self, token: str) -> dict[str, object]:
        return {
            "jti": "token-123",
            "eligible": True,
            "name": "Should be stripped",
            "sub": "citizen-record-1",
            "address": "Should also be stripped",
        }

    def check_eligibility(self, token: str) -> bool:
        return True


class VotingTokenValidationTests(unittest.TestCase):
    def test_gateway_returns_non_pii_claims(self) -> None:
        claims = VerificationGateway(client=StubClient()).validate_voting_token("token")  # type: ignore[arg-type]
        self.assertEqual(claims["jti"], "token-123")
        self.assertNotIn("name", claims)
        self.assertNotIn("sub", claims)
        self.assertNotIn("address", claims)
        self.assertNotIn("eligible", claims)


if __name__ == "__main__":
    unittest.main()
