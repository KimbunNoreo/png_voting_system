from services.voting_service.services.observer_enforcer import require_observer


def _validate_tally_payload(tally: dict[str, int]) -> None:
    if not isinstance(tally, dict):
        raise ValueError("tally payload must be a dictionary")
    if not tally:
        raise ValueError("tally payload must include at least one candidate")
    for candidate, count in tally.items():
        candidate_name = str(candidate).strip()
        if not candidate_name:
            raise ValueError("candidate name must be non-empty")
        if not isinstance(count, int):
            raise ValueError("tally counts must be integers")
        if count < 0:
            raise ValueError("tally counts cannot be negative")


def observer_tally(role: str, tally: dict[str, int]) -> dict[str, int]:
    require_observer(role)
    _validate_tally_payload(tally)
    return tally
