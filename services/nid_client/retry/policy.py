"""Retry policy definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3
    base_backoff_seconds: float = 0.5
    retryable_status_codes: tuple[int, ...] = (408, 429, 500, 502, 503, 504)