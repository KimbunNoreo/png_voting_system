"""Audit records for key access events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class KeyAccessRecord:
    key_id: str
    actor: str
    action: str
    timestamp: str


def record_key_access(key_id: str, actor: str, action: str) -> KeyAccessRecord:
    return KeyAccessRecord(key_id, actor, action, datetime.now(timezone.utc).isoformat())
