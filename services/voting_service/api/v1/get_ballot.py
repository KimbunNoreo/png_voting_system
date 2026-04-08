from services.voting_service.services.ballot_service import BallotService
def get_ballot(ballot_id: str, ballot_service: BallotService) -> dict[str, object]:
    return ballot_service.get(ballot_id).to_dict()