"""Operational helper for multi-person authorization checks."""

from __future__ import annotations


def approvals_satisfied(approvers: tuple[str, ...], minimum: int = 2) -> bool:
    return len(set(approvers)) >= minimum
