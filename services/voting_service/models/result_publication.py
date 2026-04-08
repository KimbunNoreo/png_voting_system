"""Public result commitment model."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
@dataclass(frozen=True)
class ResultPublication:
    election_id: str
    result_hash: str
    published_at: datetime
    @classmethod
    def create(cls, election_id: str, result_hash: str) -> "ResultPublication":
        return cls(election_id=election_id, result_hash=result_hash, published_at=datetime.now(timezone.utc))
    @classmethod
    def from_record(cls, *, election_id: str, result_hash: str, published_at: str) -> "ResultPublication":
        parsed = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return cls(election_id=election_id, result_hash=result_hash, published_at=parsed.astimezone(timezone.utc))
