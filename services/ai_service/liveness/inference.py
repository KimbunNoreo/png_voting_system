"""AI liveness inference remains disabled in Phase 1."""

from __future__ import annotations


def run_liveness(*args, **kwargs):
    raise RuntimeError("AI liveness inference is disabled in Phase 1")
