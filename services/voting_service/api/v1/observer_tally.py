from services.voting_service.services.observer_enforcer import require_observer
def observer_tally(role: str, tally: dict[str, int]) -> dict[str, int]:
    require_observer(role); return tally