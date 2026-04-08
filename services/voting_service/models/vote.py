"""Encrypted vote model with strict identity separation."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
@dataclass(frozen=True)
class Vote:
    vote_id: str
    election_id: str
    ballot_id: str
    encrypted_vote: str
    encrypted_key: str
    iv: str
    tag: str
    device_id: str
    device_signature: str
    token_hash: str
    kid: str
    created_at: datetime
    @classmethod
    def create(cls, **kwargs) -> "Vote":
        return cls(created_at=datetime.now(timezone.utc), **kwargs)
    @classmethod
    def from_record(cls, **kwargs) -> "Vote":
        created_at = kwargs["created_at"]
        parsed = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return cls(
            vote_id=str(kwargs["vote_id"]),
            election_id=str(kwargs["election_id"]),
            ballot_id=str(kwargs["ballot_id"]),
            encrypted_vote=str(kwargs["encrypted_vote"]),
            encrypted_key=str(kwargs["encrypted_key"]),
            iv=str(kwargs["iv"]),
            tag=str(kwargs["tag"]),
            device_id=str(kwargs["device_id"]),
            device_signature=str(kwargs["device_signature"]),
            token_hash=str(kwargs["token_hash"]),
            kid=str(kwargs["kid"]),
            created_at=parsed.astimezone(timezone.utc),
        )
    def to_dict(self) -> dict[str, object]:
        return asdict(self)
