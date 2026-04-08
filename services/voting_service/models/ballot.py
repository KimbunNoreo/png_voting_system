"""Ballot models with no embedded identity data."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
@dataclass(frozen=True)
class BallotContest:
    contest_id: str
    prompt: str
    candidates: tuple[str, ...]
    max_selections: int = 1
    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "BallotContest":
        return cls(
            contest_id=str(payload["contest_id"]),
            prompt=str(payload["prompt"]),
            candidates=tuple(str(candidate) for candidate in payload.get("candidates", ())),
            max_selections=int(payload.get("max_selections", 1)),
        )
@dataclass(frozen=True)
class Ballot:
    ballot_id: str
    election_id: str
    contests: tuple[BallotContest, ...] = field(default_factory=tuple)
    encryption_kid: str = "phase1-encryption"
    def to_dict(self) -> dict[str, object]:
        return asdict(self)
    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "Ballot":
        return cls(
            ballot_id=str(payload["ballot_id"]),
            election_id=str(payload["election_id"]),
            contests=tuple(BallotContest.from_dict(contest) for contest in payload.get("contests", ())),
            encryption_kid=str(payload.get("encryption_kid", "phase1-encryption")),
        )
