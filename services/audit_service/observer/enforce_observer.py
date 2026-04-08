"""Observer enforcement for critical actions."""

from __future__ import annotations


def observer_required(action: str) -> bool:
    return action in {"result_publication", "emergency_freeze", "manual_tally"}
