"""Public result hash publication utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from public_verification.hash_commitment import build_commitment


@dataclass(frozen=True)
class PublishedResultHash:
    election_id: str
    result_hash: str
    published_at: str


MAX_ELECTION_ID_LENGTH = 128
MAX_CANDIDATE_ID_LENGTH = 128


def _validate_election_id(election_id: str) -> str:
    normalized = election_id.strip()
    if not normalized:
        raise ValueError("Election ID is required")
    if len(normalized) > MAX_ELECTION_ID_LENGTH:
        raise ValueError("Election ID is too long")
    return normalized


def canonicalize_public_tally(tally: dict[str, int]) -> dict[str, int]:
    """Normalize tally payloads to deterministic public aggregate counts."""
    if not tally:
        raise ValueError("Public tally must not be empty")
    canonical: dict[str, int] = {}
    for candidate_id, count in sorted(tally.items()):
        normalized_candidate = str(candidate_id).strip()
        if not normalized_candidate:
            raise ValueError("Candidate ID is required")
        if len(normalized_candidate) > MAX_CANDIDATE_ID_LENGTH:
            raise ValueError("Candidate ID is too long")
        normalized_count = int(count)
        if normalized_count < 0:
            raise ValueError("Vote counts must be non-negative")
        canonical[normalized_candidate] = normalized_count
    return canonical


def publish_result_hash(election_id: str, tally: dict[str, int]) -> PublishedResultHash:
    normalized_election_id = _validate_election_id(election_id)
    canonical_tally = canonicalize_public_tally(tally)
    return PublishedResultHash(
        election_id=normalized_election_id,
        result_hash=build_commitment({"election_id": normalized_election_id, "tally": canonical_tally}),
        published_at=datetime.now(timezone.utc).isoformat(),
    )
