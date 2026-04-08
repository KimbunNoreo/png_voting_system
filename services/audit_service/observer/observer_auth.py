"""Observer authentication helpers."""

from __future__ import annotations


def require_observer_token(token: str | None) -> None:
    if not token or not token.startswith("observer-"):
        raise PermissionError("Valid observer token is required")
