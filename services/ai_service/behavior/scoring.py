"""Behavior scoring remains disabled in Phase 1."""

from __future__ import annotations


def score_behavior(*args, **kwargs):
    raise RuntimeError("Behavior scoring is disabled in Phase 1")
