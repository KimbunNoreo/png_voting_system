"""Emergency break-glass wrapper with multi-person approval checks."""

from __future__ import annotations

from scripts.multi_person_auth import approvals_satisfied


def activate_break_glass(approvers: tuple[str, ...], reason: str) -> dict[str, object]:
    if not approvals_satisfied(approvers, minimum=2):
        raise ValueError("Break-glass requires at least two distinct approvers")
    return {
        "status": "approved",
        "reason": reason,
        "approvals": len(set(approvers)),
    }
