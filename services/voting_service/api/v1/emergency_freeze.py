from services.voting_service.models.election_state import ElectionState
from services.voting_service.services.emergency_freeze_service import EmergencyFreezeService


def _validate_freeze_request(reason: str, approvals: int) -> tuple[str, int]:
    cleaned_reason = str(reason).strip()
    if not cleaned_reason:
        raise ValueError("Emergency freeze reason is required")
    if not isinstance(approvals, int):
        raise ValueError("Emergency freeze approvals must be an integer")
    if approvals < 3 or approvals > 5:
        raise ValueError("Emergency freeze requires 3 to 5 approvals")
    return cleaned_reason, approvals


def activate_freeze(state: ElectionState, reason: str, approvals: int, service: EmergencyFreezeService | None = None):
    cleaned_reason, cleaned_approvals = _validate_freeze_request(reason, approvals)
    return (service or EmergencyFreezeService()).activate(state, cleaned_reason, cleaned_approvals)


def deactivate_freeze(state: ElectionState, reason: str, approvals: int, service: EmergencyFreezeService | None = None):
    cleaned_reason, cleaned_approvals = _validate_freeze_request(reason, approvals)
    return (service or EmergencyFreezeService()).deactivate(state, cleaned_reason, cleaned_approvals)
