"""Break-glass emergency access controls."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from human_factors.multi_person_auth.session_requirements import required_approvals


@dataclass(frozen=True)
class BreakGlassActivation:
    reason: str
    approvals: int
    activated_at: str


def activate_break_glass(reason: str, approvers: tuple[str, ...]) -> BreakGlassActivation:
    minimum = required_approvals("break_glass")
    distinct_approvers = len(set(approvers))
    if distinct_approvers < minimum:
        raise ValueError("Break-glass requires at least two distinct approvers")
    return BreakGlassActivation(
        reason=reason,
        approvals=distinct_approvers,
        activated_at=datetime.now(timezone.utc).isoformat(),
    )
