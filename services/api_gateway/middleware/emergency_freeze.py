"""Emergency freeze middleware for blocking vote traffic."""

from __future__ import annotations


class EmergencyFreezeMiddleware:
    def __init__(self, frozen: bool = False) -> None:
        self.frozen = frozen

    def process(self, request: dict[str, object]) -> dict[str, object]:
        path = str(request.get("path", ""))
        if self.frozen and (path.startswith("/api/v1/vote/") or path.startswith("/api/v2/vote/")):
            raise PermissionError("Voting is frozen")
        return request
