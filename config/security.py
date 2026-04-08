"""Security configuration primitives for Phase 1 deployments."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SecurityHeaders:
    strict_transport_security: str = "max-age=63072000; includeSubDomains; preload"
    content_security_policy: str = "default-src 'self'; frame-ancestors 'none'; base-uri 'self';"
    referrer_policy: str = "no-referrer"
    x_content_type_options: str = "nosniff"
    x_frame_options: str = "DENY"
    permissions_policy: str = "camera=(), microphone=(), geolocation=()"


@dataclass(frozen=True)
class SecurityConfig:
    """Application-wide security guardrails."""

    headers: SecurityHeaders = field(default_factory=SecurityHeaders)
    csrf_cookie_secure: bool = True
    session_cookie_secure: bool = True
    secure_browser_xss_filter: bool = True
    ssl_redirect: bool = True
    require_mtls_between_services: bool = True
    allow_ai_features: bool = False
    allow_phase2_crypto: bool = False
    allow_phase3_crypto: bool = False