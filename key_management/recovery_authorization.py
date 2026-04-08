"""Threshold authorization for key recovery."""

from __future__ import annotations


def authorize_recovery(approvers: tuple[str, ...], threshold: int = 2) -> bool:
    return len(set(approvers)) >= threshold
