"""Authentication proxy for gateway requests."""

from __future__ import annotations

from typing import Any

from services.api_gateway.settings.security_settings import GatewaySecuritySettings
from services.nid_client.claim_policy import sanitize_voting_claims
from services.nid_client.exceptions import NIDValidationError
from services.nid_client.token_validator import TokenValidator


class AuthProxy:
    """Performs zero-trust bearer-token validation before routing."""

    def __init__(
        self,
        token_validator: TokenValidator | None = None,
        security_settings: GatewaySecuritySettings | None = None,
    ) -> None:
        self.security_settings = security_settings or GatewaySecuritySettings()
        self.token_validator = token_validator or TokenValidator(
            public_key=self.security_settings.token_public_key_pem,
            issuer=self.security_settings.token_issuer,
            audience=self.security_settings.token_audience,
        )

    def _extract_bearer_token(self, headers: dict[str, Any]) -> str:
        authorization = headers.get("Authorization")
        if not authorization:
            raise PermissionError("Protected gateway routes require a bearer token")
        if not isinstance(authorization, str):
            raise PermissionError("Authorization header must be a string")
        scheme, _, token = authorization.partition(" ")
        if scheme != "Bearer" or not token.strip():
            raise PermissionError("Authorization header must use Bearer token format")
        return token.strip()

    def _sanitize_claims(self, claims: dict[str, Any]) -> dict[str, Any]:
        return sanitize_voting_claims(claims)

    def process(self, request: dict[str, Any]) -> dict[str, Any]:
        headers = request.get("headers", {})
        requires_bearer = bool(request.get("route_requires_bearer_token", False))
        if requires_bearer and self.security_settings.require_vote_bearer_tokens:
            try:
                token = self._extract_bearer_token(headers)
                claims = self.token_validator.validate(token)
            except NIDValidationError as exc:
                raise PermissionError(str(exc)) from exc
            sanitized_claims = self._sanitize_claims(claims)
            token_id = sanitized_claims.get("jti")
            if not token_id:
                raise PermissionError("Validated token is missing jti")
            request["auth_context"] = {
                "token_id": token_id,
                "claims": sanitized_claims,
            }
            # Never trust caller-supplied client identity on protected routes.
            request["client_id"] = f"token:{token_id}"
        request["auth_checked"] = True
        return request
