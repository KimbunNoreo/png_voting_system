from __future__ import annotations
from dataclasses import dataclass, field
@dataclass(frozen=True)
class FraudDecision:
    allowed: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)
class DeterministicFraudService:
    def evaluate(self, *, replay_detected: bool, device_revoked: bool, within_time_window: bool) -> FraudDecision:
        reasons: list[str] = []
        if replay_detected: reasons.append("token_replay_detected")
        if device_revoked: reasons.append("device_revoked")
        if not within_time_window: reasons.append("time_sync_failed")
        return FraudDecision(allowed=not reasons, reasons=tuple(reasons))