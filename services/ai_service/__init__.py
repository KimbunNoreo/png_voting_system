"""AI service is intentionally disabled in Phase 1."""

from __future__ import annotations


def ensure_ai_disabled() -> None:
    raise RuntimeError("AI service is disabled in Phase 1 deployments")


__all__ = ["ensure_ai_disabled"]
