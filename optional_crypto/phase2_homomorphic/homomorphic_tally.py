"""Homomorphic tallying is intentionally unavailable in Phase 1."""

from __future__ import annotations


def tally(*args, **kwargs):
    raise RuntimeError("Homomorphic tallying is disabled in Phase 1")
