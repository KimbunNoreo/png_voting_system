"""Third-party verification helpers."""

from __future__ import annotations

from public_verification.hash_commitment import build_commitment


def verify_published_hash(election_id: str, tally: dict[str, int], published_hash: str) -> bool:
    return build_commitment({"election_id": election_id, "tally": tally}) == published_hash
