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


def canonicalize_public_tally(tally: dict[str, int]) -> dict[str, int]:
    """Normalize tally payloads to deterministic public aggregate counts."""

    return {str(candidate_id).strip(): int(count) for candidate_id, count in sorted(tally.items())}


def publish_result_hash(election_id: str, tally: dict[str, int]) -> PublishedResultHash:
    canonical_tally = canonicalize_public_tally(tally)
    return PublishedResultHash(
        election_id=election_id,
        result_hash=build_commitment({"election_id": election_id, "tally": canonical_tally}),
        published_at=datetime.now(timezone.utc).isoformat(),
    )
