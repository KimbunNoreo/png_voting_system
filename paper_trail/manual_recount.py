"""Manual recount helpers."""

from __future__ import annotations


def recount_ballots(ballots: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for ballot in ballots:
        counts[ballot] = counts.get(ballot, 0) + 1
    return counts
