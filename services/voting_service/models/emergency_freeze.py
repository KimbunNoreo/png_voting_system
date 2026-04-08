"""Emergency freeze audit model."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
@dataclass(frozen=True)
class EmergencyFreezeEvent:
    election_id: str
    activated: bool
    reason: str
    approvals: int
    created_at: datetime
    @classmethod
    def create(cls, election_id: str, activated: bool, reason: str, approvals: int) -> "EmergencyFreezeEvent":
        return cls(election_id, activated, reason, approvals, datetime.now(timezone.utc))
    @classmethod
    def from_record(
        cls,
        *,
        election_id: str,
        activated: int | bool,
        reason: str,
        approvals: int,
        created_at: str,
    ) -> "EmergencyFreezeEvent":
        parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return cls(
            election_id=election_id,
            activated=bool(activated),
            reason=reason,
            approvals=int(approvals),
            created_at=parsed.astimezone(timezone.utc),
        )
