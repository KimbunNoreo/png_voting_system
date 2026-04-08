"""Zero-knowledge proof generation is intentionally unavailable in Phase 1."""

from __future__ import annotations


def generate_proof(*args, **kwargs):
    raise RuntimeError("Zero-knowledge proofs are disabled in Phase 1")
