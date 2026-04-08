"""Operational wrapper for evidence bundle generation."""

from __future__ import annotations

from legal_evidence.evidence_bundle_generator import generate_evidence_bundle


def run(case_id: str, artifacts: list[dict[str, object]], actor: str) -> dict[str, object]:
    return generate_evidence_bundle(case_id, artifacts, actor).to_dict()
