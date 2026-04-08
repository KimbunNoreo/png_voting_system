"""Deterministic fallback is always active because AI is disabled."""

from __future__ import annotations


def fallback_mode() -> str:
    return "deterministic_only"
