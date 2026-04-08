"""Freeze authorization checks."""

from __future__ import annotations


def freeze_allowed(approvers: tuple[str, ...]) -> bool:
    return len(set(approvers)) >= 3
