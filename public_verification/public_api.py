"""Read-only public verification API helpers."""

from __future__ import annotations

from public_verification.result_hash_publisher import PublishedResultHash


def get_public_result(publication: PublishedResultHash) -> dict[str, str]:
    return {
        "election_id": publication.election_id,
        "result_hash": publication.result_hash,
        "published_at": publication.published_at,
    }
