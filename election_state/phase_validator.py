"""Election phase validation helpers."""

from __future__ import annotations

from election_state.state_machine import VALID_PHASES


def validate_phase(phase: str) -> str:
    if phase not in VALID_PHASES:
        raise ValueError(f"Invalid election phase: {phase}")
    return phase
