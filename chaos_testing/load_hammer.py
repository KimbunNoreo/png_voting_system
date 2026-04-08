"""Extreme load simulation helpers."""

from __future__ import annotations


def simulate_load(requests_per_second: int, limit: int) -> dict[str, object]:
    return {"scenario": "load_hammer", "requests_per_second": requests_per_second, "limit_exceeded": requests_per_second > limit}
