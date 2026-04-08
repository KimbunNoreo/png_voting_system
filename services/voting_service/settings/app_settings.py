from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os


def _runtime_path(filename: str) -> str:
    runtime_dir = Path(os.getenv("VOTING_RUNTIME_DIR", "data/runtime"))
    return str(runtime_dir / filename)


@dataclass(frozen=True)
class VotingAppSettings:
    """Application-level settings for secure voting service assembly."""

    service_name: str = "voting_service"
    public_results_enabled: bool = True
    observers_enabled: bool = True
    use_durable_token_registry: bool = field(
        default_factory=lambda: os.getenv("VOTING_USE_DURABLE_TOKEN_REGISTRY", "true").lower() == "true"
    )
    use_durable_result_publications: bool = field(
        default_factory=lambda: os.getenv("VOTING_USE_DURABLE_RESULT_PUBLICATIONS", "true").lower() == "true"
    )
    use_durable_ballot_registry: bool = field(
        default_factory=lambda: os.getenv("VOTING_USE_DURABLE_BALLOT_REGISTRY", "true").lower() == "true"
    )
    use_durable_election_state: bool = field(
        default_factory=lambda: os.getenv("VOTING_USE_DURABLE_ELECTION_STATE", "true").lower() == "true"
    )
    use_durable_device_revocation_registry: bool = field(
        default_factory=lambda: os.getenv("VOTING_USE_DURABLE_DEVICE_REVOCATION_REGISTRY", "true").lower() == "true"
    )
    use_durable_emergency_freeze_history: bool = field(
        default_factory=lambda: os.getenv("VOTING_USE_DURABLE_EMERGENCY_FREEZE_HISTORY", "true").lower() == "true"
    )
    use_durable_rate_limits: bool = field(
        default_factory=lambda: os.getenv("VOTING_USE_DURABLE_RATE_LIMITS", "true").lower() == "true"
    )
    use_durable_vote_repository: bool = field(
        default_factory=lambda: os.getenv("VOTING_USE_DURABLE_VOTE_REPOSITORY", "true").lower() == "true"
    )
    use_durable_control_plane: bool = field(
        default_factory=lambda: os.getenv("VOTING_USE_DURABLE_CONTROL_PLANE", "true").lower() == "true"
    )
    used_token_registry_path: str = field(default_factory=lambda: _runtime_path("used_tokens.sqlite3"))
    token_replay_registry_path: str = field(default_factory=lambda: _runtime_path("token_replay.sqlite3"))
    result_publication_path: str = field(default_factory=lambda: _runtime_path("result_publications.sqlite3"))
    ballot_registry_path: str = field(default_factory=lambda: _runtime_path("ballots.sqlite3"))
    election_state_path: str = field(default_factory=lambda: _runtime_path("election_state.sqlite3"))
    device_revocation_path: str = field(default_factory=lambda: _runtime_path("device_revocations.sqlite3"))
    emergency_freeze_history_path: str = field(default_factory=lambda: _runtime_path("emergency_freeze.sqlite3"))
    rate_limit_path: str = field(default_factory=lambda: _runtime_path("rate_limits.sqlite3"))
    vote_repository_path: str = field(default_factory=lambda: _runtime_path("votes.sqlite3"))
    control_plane_path: str = field(default_factory=lambda: _runtime_path("control_plane.sqlite3"))
    control_plane_phase_audit_path: str = field(default_factory=lambda: _runtime_path("control_plane_phase_audit.sqlite3"))
