from dataclasses import dataclass
@dataclass(frozen=True)
class BallotSettings:
    allow_write_in_candidates: bool = False
    require_contest_validation: bool = True