"""Zero-knowledge proof verification is intentionally unavailable in Phase 1."""

from __future__ import annotations


def verify_proof(*args, **kwargs):
    raise RuntimeError("Zero-knowledge proofs are disabled in Phase 1")
