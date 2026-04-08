"""Consumed token registry entries."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
@dataclass(frozen=True)
class UsedToken:
    token_hash: str
    device_id: str
    consumed_at: datetime
    @classmethod
    def create(cls, token_hash: str, device_id: str) -> "UsedToken":
        return cls(token_hash=token_hash, device_id=device_id, consumed_at=datetime.now(timezone.utc))
    @classmethod
    def from_record(cls, *, token_hash: str, device_id: str, consumed_at: str) -> "UsedToken":
        parsed = datetime.fromisoformat(consumed_at.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return cls(token_hash=token_hash, device_id=device_id, consumed_at=parsed.astimezone(timezone.utc))
