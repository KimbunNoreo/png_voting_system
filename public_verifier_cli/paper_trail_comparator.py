"""Compare paper trail records against digital tallies."""

from __future__ import annotations


def compare_counts(paper_counts: dict[str, int], digital_counts: dict[str, int]) -> dict[str, int]:
    keys = set(paper_counts) | set(digital_counts)
    return {key: paper_counts.get(key, 0) - digital_counts.get(key, 0) for key in keys}
