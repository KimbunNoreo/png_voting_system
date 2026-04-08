from __future__ import annotations

from services.nid_client import NIDClient
from services.nid_client.claim_policy import sanitize_voting_claims


class VerificationGateway:
    """Validate NID tokens while enforcing identity-vote separation."""

    def __init__(self, client: NIDClient | None = None) -> None:
        self.client = client or NIDClient()

    def validate_voting_token(self, token: str) -> dict[str, object]:
        claims = self.client.validate_token(token)
        if not self.client.check_eligibility(token):
            raise ValueError("Token is not eligible for voting")
        sanitized_claims = sanitize_voting_claims(claims)
        if "jti" not in sanitized_claims:
            raise ValueError("Validated token is missing jti")
        return sanitized_claims
