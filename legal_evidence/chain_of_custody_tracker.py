"""Chain of custody tracking for legal evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CustodyEvent:
    actor: str
    action: str
    timestamp: str


def record_custody_event(actor: str, action: str) -> CustodyEvent:
    return CustodyEvent(actor=actor, action=action, timestamp=datetime.now(timezone.utc).isoformat())
