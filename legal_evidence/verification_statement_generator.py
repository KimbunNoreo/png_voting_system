"""Human-readable verification statements for court submissions."""

from __future__ import annotations


def generate_statement(case_id: str, verified: bool) -> str:
    verdict = "verified" if verified else "not verified"
    return f"Evidence package for case {case_id} has been {verdict}."
