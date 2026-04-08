"""Phase 1 rollout guardrail helper."""

from __future__ import annotations


def enforce_phase1_only(requested_phase: str) -> str:
    if requested_phase.lower() != "phase1":
        raise ValueError("Only Phase 1 rollout is permitted")
    return "phase1"
