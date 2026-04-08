"""Gateway application assembly for SecureVote PNG."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from services.api_gateway.auth_proxy import AuthProxy
from services.api_gateway.middleware.api_version_router import APIVersionRouter
from services.api_gateway.middleware.emergency_freeze import EmergencyFreezeMiddleware
from services.api_gateway.middleware.ip_filter import IPFilterMiddleware
from services.api_gateway.middleware.mTLS_verifier import MTLSVerifierMiddleware
from services.api_gateway.middleware.request_sanitizer import RequestSanitizerMiddleware
from services.api_gateway.middleware.tls_enforcement import TLSEnforcementMiddleware
from services.api_gateway.rate_limit import SlidingWindowRateLimiter
from services.api_gateway.routing import GatewayRouter
from services.api_gateway.threat_detection import ThreatDetector


@dataclass
class GatewayApplication:
    """Lightweight gateway pipeline for zero-trust request handling."""

    router: GatewayRouter
    auth_proxy: AuthProxy = field(default_factory=AuthProxy)
    rate_limiter: SlidingWindowRateLimiter = field(default_factory=SlidingWindowRateLimiter)
    threat_detector: ThreatDetector = field(default_factory=ThreatDetector)
    tls_enforcement: TLSEnforcementMiddleware = field(default_factory=TLSEnforcementMiddleware)
    sanitizer: RequestSanitizerMiddleware = field(default_factory=RequestSanitizerMiddleware)
    ip_filter: IPFilterMiddleware = field(default_factory=IPFilterMiddleware)
    mtls_verifier: MTLSVerifierMiddleware = field(default_factory=MTLSVerifierMiddleware)
    version_router: APIVersionRouter = field(default_factory=APIVersionRouter)
    emergency_freeze: EmergencyFreezeMiddleware = field(default_factory=EmergencyFreezeMiddleware)

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Apply middleware and return a routed request descriptor."""

        request = self.tls_enforcement.process(request)
        request = self.sanitizer.process(request)
        request["path"] = self.router.normalize_path(str(request["path"]))
        request = self.ip_filter.process(request)
        request = self.mtls_verifier.process(request)
        request = self.version_router.process(request)
        self.threat_detector.inspect(request)
        route = self.router.resolve(str(request["path"]), str(request.get("method", "GET")))
        request["route_destination"] = route.destination
        request["route_bucket"] = route.rate_limit_bucket
        request["route_requires_bearer_token"] = route.requires_bearer_token
        request = self.emergency_freeze.process(request)
        request = self.auth_proxy.process(request)
        self.rate_limiter.enforce(request)
        return {"route": route.destination, "request": request}
