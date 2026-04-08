"""Key rotation policy configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KeyRotationSchedule:
    signing_rotation_days: int = 90
    encryption_rotation_days: int = 90
    grace_period_days: int = 14
    emergency_rotation_enabled: bool = True