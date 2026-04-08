"""Audit retention policy."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuditRetentionPolicy:
    retention_days: int = 3650
    worm_required: bool = True
    legal_hold_supported: bool = True