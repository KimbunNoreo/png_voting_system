"""Voting rate-limit configuration."""

from __future__ import annotations

from dataclasses import dataclass

from config.constants import MAX_VOTES_PER_DEVICE_PER_MINUTE, MAX_VOTES_PER_TOKEN_PER_MINUTE


@dataclass(frozen=True)
class VotingRateLimitConfig:
    per_token_per_minute: int = MAX_VOTES_PER_TOKEN_PER_MINUTE
    per_device_per_minute: int = MAX_VOTES_PER_DEVICE_PER_MINUTE
    burst_window_seconds: int = 60