"""Generate non-production sample voting data without storing identity."""

from __future__ import annotations

from services.voting_service.models.ballot import Ballot, BallotContest


def build_sample_ballot(election_id: str = "sample-election") -> Ballot:
    return Ballot(
        ballot_id="sample-ballot",
        election_id=election_id,
        contests=(
            BallotContest(
                contest_id="president",
                prompt="Select one candidate",
                candidates=("candidate-a", "candidate-b", "candidate-c"),
            ),
        ),
    )
