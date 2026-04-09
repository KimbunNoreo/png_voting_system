"""Gateway operational settings."""

from __future__ import annotations

from dataclasses import dataclass, field
import os

from config.constants import DEFAULT_CONNECT_TIMEOUT_SECONDS, DEFAULT_REQUEST_TIMEOUT_SECONDS


def _read_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


@dataclass(frozen=True)
class GatewaySettings:
    """Operational controls for the zero-trust API gateway."""

    request_timeout_seconds: int = field(
        default_factory=lambda: _read_int("GATEWAY_REQUEST_TIMEOUT_SECONDS", DEFAULT_REQUEST_TIMEOUT_SECONDS)
    )
    connect_timeout_seconds: int = field(
        default_factory=lambda: _read_int("GATEWAY_CONNECT_TIMEOUT_SECONDS", DEFAULT_CONNECT_TIMEOUT_SECONDS)
    )
    rate_limit_window_seconds: int = field(default_factory=lambda: _read_int("GATEWAY_RATE_LIMIT_WINDOW_SECONDS", 60))
    default_requests_per_minute: int = field(default_factory=lambda: _read_int("GATEWAY_DEFAULT_REQUESTS_PER_MINUTE", 60))
    nid_requests_per_minute: int = field(default_factory=lambda: _read_int("GATEWAY_NID_REQUESTS_PER_MINUTE", 30))
    vote_requests_per_minute: int = field(default_factory=lambda: _read_int("GATEWAY_VOTE_REQUESTS_PER_MINUTE", 10))
    vote_public_requests_per_minute: int = field(
        default_factory=lambda: _read_int("GATEWAY_VOTE_PUBLIC_REQUESTS_PER_MINUTE", 30)
    )
    vote_token_requests_per_minute: int = field(
        default_factory=lambda: _read_int("GATEWAY_VOTE_TOKEN_REQUESTS_PER_MINUTE", 5)
    )
    vote_device_requests_per_minute: int = field(
        default_factory=lambda: _read_int("GATEWAY_VOTE_DEVICE_REQUESTS_PER_MINUTE", 10)
    )
    use_redis_rate_limiter: bool = field(
        default_factory=lambda: os.getenv("GATEWAY_USE_REDIS_RATE_LIMITER", "false").lower() == "true"
    )
