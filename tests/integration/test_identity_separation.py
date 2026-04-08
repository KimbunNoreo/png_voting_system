from __future__ import annotations

import unittest

from services.voting_service.services.verification_gateway import VerificationGateway


class StubClient:
    def validate_token(self, token: str) -> dict[str, object]:
        return {
            "jti": "token-1",
            "name": "Sensitive Name",
            "address": "Sensitive Address",
            "sub": "nid-subject-123",
            "biometrics": {"face": "template"},
            "eligible": True,
        }

    def check_eligibility(self, token: str) -> bool:
        return True


class IdentitySeparationTests(unittest.TestCase):
    def test_gateway_strips_pii_from_claims(self) -> None:
        gateway = VerificationGateway(client=StubClient())  # type: ignore[arg-type]
        claims = gateway.validate_voting_token("token")
        self.assertIn("jti", claims)
        self.assertNotIn("name", claims)
        self.assertNotIn("address", claims)
        self.assertNotIn("sub", claims)
        self.assertNotIn("biometrics", claims)
        self.assertNotIn("eligible", claims)


if __name__ == "__main__":
    unittest.main()
