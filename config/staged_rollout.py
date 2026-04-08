"""Phase gate configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StagedRolloutConfig:
    phase1_only: bool = True
    allow_phase2_artifacts: bool = False
    allow_phase3_artifacts: bool = False