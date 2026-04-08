"""Result disclosure with commitment verification."""

from __future__ import annotations

from public_verification.hash_commitment import build_commitment
from public_verification.result_hash_publisher import PublishedResultHash, canonicalize_public_tally


def disclose_results(publication: PublishedResultHash, tally: dict[str, int]) -> dict[str, object]:
    canonical_tally = canonicalize_public_tally(tally)
    recomputed = build_commitment({"election_id": publication.election_id, "tally": canonical_tally})
    return {
        "election_id": publication.election_id,
        "verified": recomputed == publication.result_hash,
        "tally": canonical_tally,
        "published_at": publication.published_at,
    }
