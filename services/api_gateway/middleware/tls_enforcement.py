"""TLS enforcement middleware."""

from __future__ import annotations


class TLSEnforcementMiddleware:
    def process(self, request: dict[str, object]) -> dict[str, object]:
        if not request.get("is_tls", False):
            raise PermissionError("TLS is required")
        return request
