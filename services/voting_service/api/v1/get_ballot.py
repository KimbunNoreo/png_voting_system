from services.voting_service.services.ballot_service import BallotService


def _require_non_empty_ballot_id(ballot_id: str) -> str:
    value = str(ballot_id).strip()
    if not value:
        raise ValueError("ballot_id is required")
    return value


def get_ballot(ballot_id: str, ballot_service: BallotService) -> dict[str, object]:
    return ballot_service.get(_require_non_empty_ballot_id(ballot_id)).to_dict()
