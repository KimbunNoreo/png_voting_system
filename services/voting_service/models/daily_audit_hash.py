"""Daily audit hash model."""
from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class DailyAuditHash:
    device_id: str
    day: str
    digest: str