"""AI anomaly model remains disabled in Phase 1."""

from __future__ import annotations


def score_anomaly(*args, **kwargs):
    raise RuntimeError("AI anomaly scoring is disabled in Phase 1")
