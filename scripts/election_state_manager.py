"""Operational wrapper for election phase transitions."""

from __future__ import annotations

from election_state.audit_phase_changes import record_phase_change
from election_state.state_machine import ElectionStateMachine


def transition(machine: ElectionStateMachine, next_phase: str, approvers: tuple[str, ...]) -> dict[str, object]:
    previous_phase = machine.phase
    machine.transition_to(next_phase)
    audit = record_phase_change(machine.election_id, previous_phase, next_phase, approvers)
    return {"phase": machine.phase, "audit": audit}
