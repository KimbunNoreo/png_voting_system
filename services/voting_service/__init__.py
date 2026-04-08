"""Voting service package."""

__all__ = ["cast_vote", "VotingServiceDependencies", "build_voting_dependencies"]


def __getattr__(name: str):
    if name == "cast_vote":
        from services.voting_service.api.v1.cast_vote import cast_vote

        return cast_vote
    if name in {"VotingServiceDependencies", "build_voting_dependencies"}:
        from services.voting_service.factory import VotingServiceDependencies, build_voting_dependencies

        return {
            "VotingServiceDependencies": VotingServiceDependencies,
            "build_voting_dependencies": build_voting_dependencies,
        }[name]
    raise AttributeError(name)
