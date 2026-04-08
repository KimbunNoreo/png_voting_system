"""IP filtering middleware."""

from __future__ import annotations

from ipaddress import ip_address, ip_network

from services.api_gateway.settings.security_settings import GatewaySecuritySettings


class IPFilterMiddleware:
    """Reject traffic that does not originate from approved network ranges."""

    def __init__(
        self,
        blocked_ips: set[str] | None = None,
        security_settings: GatewaySecuritySettings | None = None,
    ) -> None:
        self.blocked_ips = blocked_ips or set()
        self.security_settings = security_settings or GatewaySecuritySettings()
        self._allowed_networks = tuple(ip_network(cidr, strict=False) for cidr in self.security_settings.allowed_cidrs)

    def process(self, request: dict[str, object]) -> dict[str, object]:
        ip = str(request.get("ip", ""))
        if not ip:
            raise PermissionError("Source IP is required")
        if ip in self.blocked_ips:
            raise PermissionError("Source IP is blocked")
        parsed_ip = ip_address(ip)
        if self._allowed_networks and not any(parsed_ip in network for network in self._allowed_networks):
            raise PermissionError("Source IP is outside the gateway allowlist")
        return request
