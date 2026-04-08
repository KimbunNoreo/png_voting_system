"""Simplified threshold-based key share handling."""

from __future__ import annotations


def split_secret(secret: str, shares: int = 3) -> list[str]:
    return [f"{index}:{secret}" for index in range(1, shares + 1)]


def recover_secret(parts: list[str], threshold: int = 2) -> str:
    if len(parts) < threshold:
        raise ValueError("Not enough shares to recover secret")
    return parts[0].split(":", 1)[1]
