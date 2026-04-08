"""Token validation helpers for NID-issued JWTs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import jwt

from services.nid_client.exceptions import NIDValidationError


class TokenValidator:
    """Validate externally issued RS256 tokens without storing identity payloads."""

    def __init__(self, public_key: str | None = None, issuer: str | None = None, audience: str | None = None) -> None:
        self.public_key = public_key
        self.issuer = issuer
        self.audience = audience

    def decode(self, token: str) -> dict[str, Any]:
        options = {"require": ["exp", "iat", "jti"]}
        try:
            if self.public_key:
                return jwt.decode(
                    token,
                    self.public_key,
                    algorithms=["RS256"],
                    issuer=self.issuer,
                    audience=self.audience,
                    options=options,
                )
            return jwt.decode(token, options={"verify_signature": False, **options}, algorithms=["RS256"])
        except jwt.PyJWTError as exc:
            raise NIDValidationError(f"Invalid NID token: {exc}") from exc

    def validate_expiry(self, claims: dict[str, Any]) -> None:
        exp = claims.get("exp")
        if exp is None:
            raise NIDValidationError("NID token missing expiry")
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        if expires_at <= datetime.now(timezone.utc):
            raise NIDValidationError("NID token is expired")

    def validate(self, token: str) -> dict[str, Any]:
        claims = self.decode(token)
        self.validate_expiry(claims)
        return claims