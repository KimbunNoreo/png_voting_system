"""Session approval requirements by operation."""

from __future__ import annotations


def required_approvals(operation: str) -> int:
    if operation == "global_freeze":
        return 3
    if operation in {"break_glass", "phase_change", "key_recovery", "offline_sync_conflict_flush"}:
        return 2
    return 1
