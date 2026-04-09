from __future__ import annotations

from services.nid_client import NIDClient
from services.nid_client.claim_policy import sanitize_voting_claims


class VerificationGateway:
    """Validate NID tokens while enforcing identity-vote separation."""

    def __init__(self, client: NIDClient | None = None) -> None:
        self.client = client or NIDClient()

    def validate_voting_token(self, token: str) -> dict[str, object]:
        token_value = str(token).strip()
        if not token_value:
            raise ValueError("Voting token is required")

        claims = self.client.validate_token(token_value)
        if not isinstance(claims, dict):
            raise ValueError("Token validation returned invalid claim payload")

        eligibility = self.client.check_eligibility(token_value)
        if not isinstance(eligibility, bool):
            raise ValueError("Eligibility check returned non-boolean result")
        if not eligibility:
            raise ValueError("Token is not eligible for voting")

        sanitized_claims = sanitize_voting_claims(claims)
        jti = sanitized_claims.get("jti")
        if not isinstance(jti, str) or not jti.strip():
            raise ValueError("Validated token is missing jti")
        return sanitized_claims
