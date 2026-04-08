"""Paper-to-digital reconciliation helpers."""

from __future__ import annotations

from public_verifier_cli.paper_trail_comparator import compare_counts


def reconcile(paper_counts: dict[str, int], digital_counts: dict[str, int]) -> dict[str, int]:
    return compare_counts(paper_counts, digital_counts)
