"""Paillier support is intentionally unavailable in Phase 1."""

from __future__ import annotations


def encrypt(*args, **kwargs):
    raise RuntimeError("Homomorphic encryption is disabled in Phase 1")
