"""Append-only audit ledger entries for voting events."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
@dataclass(frozen=True)
class LedgerEntry:
    entry_id: str
    event_type: str
    payload_hash: str
    previous_hash: str
    created_at: datetime
    @classmethod
    def create(cls, entry_id: str, event_type: str, payload_hash: str, previous_hash: str) -> "LedgerEntry":
        return cls(entry_id, event_type, payload_hash, previous_hash, datetime.now(timezone.utc))