from services.voting_service.models.result_publication import ResultPublication


def _validate_publication(publication: ResultPublication) -> None:
    if not publication.election_id.strip():
        raise ValueError("publication.election_id must be non-empty")
    if not publication.result_hash.strip():
        raise ValueError("publication.result_hash must be non-empty")


def public_result(publication: ResultPublication) -> dict[str, object]:
    _validate_publication(publication)
    return {"election_id": publication.election_id, "result_hash": publication.result_hash, "published_at": publication.published_at.isoformat()}
