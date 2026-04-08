"""AI model settings guarded for Phase 1."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DisabledAIModelSettings:
    enabled: bool = False
    reason: str = "Phase 1 forbids AI-assisted decision making"
