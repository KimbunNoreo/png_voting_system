"""Incident reporting helpers."""

from __future__ import annotations


def report_incident(actor: str, summary: str) -> dict[str, str]:
    return {"actor": actor, "summary": summary}
