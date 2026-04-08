"""Court submission formatting helpers."""

from __future__ import annotations


def format_for_court(bundle: dict[str, object]) -> dict[str, object]:
    return {"submission_type": "court_evidence_bundle", "bundle": bundle}
