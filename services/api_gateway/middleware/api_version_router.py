"""API version normalization middleware."""

from __future__ import annotations


class APIVersionRouter:
    def process(self, request: dict[str, object]) -> dict[str, object]:
        path = str(request.get("path", ""))
        if path.startswith("/api/v1/"):
            request["api_version"] = "v1"
        elif path.startswith("/api/v2/"):
            request["api_version"] = "v2"
        else:
            raise ValueError("Unsupported API version")
        return request
