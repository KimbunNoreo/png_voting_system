"""Simple geographic density checks without identity linkage."""

def excessive_precinct_velocity(votes_in_window: int, max_allowed: int) -> bool:
    return votes_in_window > max_allowed