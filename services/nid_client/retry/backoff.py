"""Backoff helpers for retried NID requests."""

from __future__ import annotations


def exponential_backoff(base_seconds: float, attempt: int, max_seconds: float = 5.0) -> float:
    return min(base_seconds * (2 ** max(attempt - 1, 0)), max_seconds)