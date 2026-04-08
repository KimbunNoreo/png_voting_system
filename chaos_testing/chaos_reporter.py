"""Chaos test report generation."""

from __future__ import annotations


def build_report(results: list[dict[str, object]]) -> dict[str, object]:
    return {
        "scenario_count": len(results),
        "degraded_scenarios": [result["scenario"] for result in results if result.get("degraded") or result.get("failed") or result.get("fallback_required") or result.get("recovery_required") or result.get("limit_exceeded")],
    }
