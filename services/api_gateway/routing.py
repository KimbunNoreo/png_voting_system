"""Deterministic route resolution for gateway traffic."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RouteDefinition:
    """Immutable route policy describing a trusted upstream."""

    prefix: str
    destination: str
    requires_bearer_token: bool = False
    allowed_methods: tuple[str, ...] = ("GET", "POST")
    rate_limit_bucket: str = "default"


@dataclass
class GatewayRouter:
    """Maps API paths to trusted upstream domains and route policy."""

    routes: tuple[RouteDefinition, ...] = field(
        default_factory=lambda: (
            RouteDefinition(
                prefix="/api/v1/nid/",
                destination="external_nid",
                allowed_methods=("GET", "POST"),
                rate_limit_bucket="nid",
            ),
            RouteDefinition(
                prefix="/api/v1/vote/",
                destination="voting_service",
                requires_bearer_token=True,
                allowed_methods=("GET", "POST"),
                rate_limit_bucket="vote",
            ),
            RouteDefinition(
                prefix="/api/v2/vote/",
                destination="reserved_v2",
                requires_bearer_token=True,
                allowed_methods=("GET", "POST"),
                rate_limit_bucket="vote",
            ),
        )
    )

    def normalize_path(self, path: str) -> str:
        normalized = "/" + "/".join(segment for segment in path.split("/") if segment)
        if not normalized.startswith("/api/"):
            raise ValueError("Gateway path must begin with /api/")
        if ".." in normalized.split("/"):
            raise ValueError("Path traversal is not allowed")
        return normalized + ("/" if path.endswith("/") and normalized != "/" else "")

    def resolve(self, path: str, method: str = "GET") -> RouteDefinition:
        normalized_path = self.normalize_path(path)
        normalized_method = method.upper()
        for route in self.routes:
            if normalized_path.startswith(route.prefix):
                if normalized_method not in route.allowed_methods:
                    raise ValueError(f"Method {normalized_method} is not allowed for path: {normalized_path}")
                return route
        raise ValueError(f"No route configured for path: {normalized_path}")
