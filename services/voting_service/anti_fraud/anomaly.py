"""Deterministic anomaly scoring for Phase 1 advisory use only."""

def anomaly_score(votes_per_minute: int, threshold: int = 10) -> int:
    return max(votes_per_minute - threshold, 0)