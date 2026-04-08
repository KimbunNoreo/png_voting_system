"""Replay detection audit entries."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
@dataclass(frozen=True)
class TokenReplayAttempt:
    token_hash: str
    original_device_id: str
    replay_device_id: str
    detected_at: datetime
    @classmethod
    def create(cls, token_hash: str, original_device_id: str, replay_device_id: str) -> "TokenReplayAttempt":
        return cls(token_hash, original_device_id, replay_device_id, datetime.now(timezone.utc))
    @classmethod
    def from_record(
        cls,
        *,
        token_hash: str,
        original_device_id: str,
        replay_device_id: str,
        detected_at: str,
    ) -> "TokenReplayAttempt":
        parsed = datetime.fromisoformat(detected_at.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return cls(
            token_hash=token_hash,
            original_device_id=original_device_id,
            replay_device_id=replay_device_id,
            detected_at=parsed.astimezone(timezone.utc),
        )
