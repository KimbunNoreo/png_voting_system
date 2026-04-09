"""Freeze authorization checks."""

from __future__ import annotations


def freeze_allowed(approvers: tuple[str, ...]) -> bool:
    unique_approvers = {approver.strip() for approver in approvers if approver.strip()}
    return 3 <= len(unique_approvers) <= 5
