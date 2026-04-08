"""Emergency override authorization."""

from __future__ import annotations


def emergency_override_allowed(approvers: tuple[str, ...]) -> bool:
    return len(set(approvers)) >= 4
