"""Revoked device model."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
@dataclass(frozen=True)
class DeviceRevocation:
    device_id: str
    reason: str
    revoked_at: datetime
    @classmethod
    def create(cls, device_id: str, reason: str) -> "DeviceRevocation":
        return cls(device_id=device_id, reason=reason, revoked_at=datetime.now(timezone.utc))
    @classmethod
    def from_record(cls, *, device_id: str, reason: str, revoked_at: str) -> "DeviceRevocation":
        parsed = datetime.fromisoformat(revoked_at.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return cls(device_id=device_id, reason=reason, revoked_at=parsed.astimezone(timezone.utc))
