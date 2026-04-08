from services.voting_service.models.election_state import ElectionState
from services.voting_service.services.emergency_freeze_service import EmergencyFreezeService
def activate_freeze(state: ElectionState, reason: str, approvals: int, service: EmergencyFreezeService | None = None):
    return (service or EmergencyFreezeService()).activate(state, reason, approvals)