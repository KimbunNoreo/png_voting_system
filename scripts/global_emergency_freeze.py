"""Operational wrapper for global emergency freeze."""

from __future__ import annotations

from services.voting_service.models.election_state import ElectionState
from services.voting_service.services.emergency_freeze_service import EmergencyFreezeService


def activate(election_id: str, phase: str, reason: str, approvals: int) -> dict[str, object]:
    service = EmergencyFreezeService()
    state = ElectionState(election_id=election_id, phase=phase, freeze_active=False)
    new_state, event = service.activate(state, reason, approvals)
    return {"state": new_state, "event": event}
