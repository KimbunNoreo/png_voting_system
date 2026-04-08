"""Safe claim policy for crossing from external NID into voting services."""

from __future__ import annotations

from typing import Any


# Only claims required for token lifecycle validation and replay prevention may
# cross the identity boundary into the voting system.
SAFE_VOTING_CLAIMS = frozenset({"jti", "exp", "iat", "iss", "aud", "nbf", "kid"})


def sanitize_voting_claims(claims: dict[str, Any]) -> dict[str, Any]:
    """Return the minimal non-identity claim set allowed inside voting flows."""

    return {key: value for key, value in claims.items() if key in SAFE_VOTING_CLAIMS}
