"""Operational script wrapper for result hash publication."""

from __future__ import annotations

from public_verification.result_hash_publisher import publish_result_hash


def run(election_id: str, tally: dict[str, int]) -> dict[str, str]:
    publication = publish_result_hash(election_id, tally)
    return {
        "election_id": publication.election_id,
        "result_hash": publication.result_hash,
        "published_at": publication.published_at,
    }
