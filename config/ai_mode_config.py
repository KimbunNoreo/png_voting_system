"""AI mode configuration for strict Phase 1 enforcement."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AIModeConfig:
    enabled: bool = False
    advisory_only: bool = True
    deterministic_fallback_required: bool = True