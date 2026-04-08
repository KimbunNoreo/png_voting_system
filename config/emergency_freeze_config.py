"""Emergency freeze governance configuration."""

from __future__ import annotations

from dataclasses import dataclass

from config.constants import EMERGENCY_FREEZE_APPROVALS


@dataclass(frozen=True)
class EmergencyFreezeConfig:
    enabled: bool = False
    required_approvals: int = EMERGENCY_FREEZE_APPROVALS
    audit_reason_required: bool = True