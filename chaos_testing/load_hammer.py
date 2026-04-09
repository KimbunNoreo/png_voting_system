"""Extreme load simulation helpers."""

from __future__ import annotations


def simulate_load(requests_per_second: int, limit: int) -> dict[str, object]:
    if requests_per_second < 0:
        raise ValueError("Requests per second must be non-negative")
    if limit <= 0:
        raise ValueError("Limit must be positive")
    return {"scenario": "load_hammer", "requests_per_second": requests_per_second, "limit_exceeded": requests_per_second > limit}
