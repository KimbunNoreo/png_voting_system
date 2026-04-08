"""Strict election state machine for SecureVote PNG."""

from __future__ import annotations

from dataclasses import dataclass, field


VALID_PHASES: tuple[str, ...] = (
    "registration",
    "verification",
    "voting",
    "locked",
    "counting",
    "finalized",
)


@dataclass
class ElectionStateMachine:
    """Enforces valid phase transitions and freeze rules."""

    election_id: str
    phase: str = "registration"
    freeze_active: bool = False
    _transitions: dict[str, tuple[str, ...]] = field(
        default_factory=lambda: {
            "registration": ("verification",),
            "verification": ("voting",),
            "voting": ("locked",),
            "locked": ("counting",),
            "counting": ("finalized",),
            "finalized": (),
        }
    )

    def assert_operation_allowed(self, operation: str) -> None:
        if self.freeze_active and operation in {"cast_vote", "get_ballot"}:
            raise ValueError("Operation blocked while global freeze is active")
        if operation == "cast_vote" and self.phase != "voting":
            raise ValueError("Votes may only be cast during the voting phase")

    def transition_to(self, next_phase: str) -> str:
        if next_phase not in VALID_PHASES:
            raise ValueError(f"Unknown election phase: {next_phase}")
        allowed = self._transitions[self.phase]
        if next_phase not in allowed:
            raise ValueError(f"Invalid phase transition from {self.phase} to {next_phase}")
        self.phase = next_phase
        return self.phase

    def activate_freeze(self) -> None:
        self.freeze_active = True

    def clear_freeze(self) -> None:
        self.freeze_active = False
