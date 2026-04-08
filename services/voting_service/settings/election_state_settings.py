from dataclasses import dataclass
@dataclass(frozen=True)
class ElectionStateSettings:
    valid_phases: tuple[str, ...] = ("registration", "verification", "voting", "locked", "counting", "finalized")
    voting_phase: str = "voting"