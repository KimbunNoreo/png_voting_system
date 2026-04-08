"""Election phase state."""
from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class ElectionState:
    election_id: str
    phase: str
    freeze_active: bool = False
    @classmethod
    def from_record(cls, *, election_id: str, phase: str, freeze_active: int | bool) -> "ElectionState":
        return cls(election_id=election_id, phase=phase, freeze_active=bool(freeze_active))
