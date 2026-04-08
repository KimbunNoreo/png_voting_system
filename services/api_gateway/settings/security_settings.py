"""Gateway security settings."""

from __future__ import annotations

from dataclasses import dataclass, field
import os


def _csv(name: str, default: str) -> tuple[str, ...]:
    value = os.getenv(name, default)
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class GatewaySecuritySettings:
    """Security controls for gateway request admission."""

    allowed_cidrs: tuple[str, ...] = field(default_factory=lambda: _csv("GATEWAY_ALLOWED_CIDRS", "127.0.0.1/32"))
    require_tls: bool = True
    require_mtls: bool = True
    blocked_user_agents: tuple[str, ...] = field(default_factory=lambda: _csv("GATEWAY_BLOCKED_USER_AGENTS", "sqlmap,nikto"))
    require_vote_bearer_tokens: bool = True
    token_public_key_pem: str | None = field(default_factory=lambda: os.getenv("NID_JWT_PUBLIC_KEY_PEM"))
    token_issuer: str | None = field(default_factory=lambda: os.getenv("NID_JWT_ISSUER"))
    token_audience: str | None = field(default_factory=lambda: os.getenv("NID_JWT_AUDIENCE"))
    trusted_client_certificate_subjects: tuple[str, ...] = field(
        default_factory=lambda: _csv(
            "GATEWAY_TRUSTED_CLIENT_CERT_SUBJECTS",
            "CN=voting-service.internal,O=SecureVote PNG,C=PG,CN=nid-client.internal,O=SecureVote PNG,C=PG",
        )
    )
    trusted_client_spiffe_ids: tuple[str, ...] = field(
        default_factory=lambda: _csv(
            "GATEWAY_TRUSTED_CLIENT_SPIFFE_IDS",
            "spiffe://securevote/internal/voting-service,spiffe://securevote/internal/nid-client",
        )
    )
    require_certificate_chain_validation: bool = True
    require_client_auth_eku: bool = True
