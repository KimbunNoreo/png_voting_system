"""Observer verification checks."""

from __future__ import annotations


def observer_verified(observer_key: str) -> bool:
    return observer_key.startswith("observer-")
