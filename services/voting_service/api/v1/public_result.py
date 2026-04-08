from services.voting_service.models.result_publication import ResultPublication
def public_result(publication: ResultPublication) -> dict[str, object]:
    return {"election_id": publication.election_id, "result_hash": publication.result_hash, "published_at": publication.published_at.isoformat()}