"""Voting service dependency assembly for production-style usage."""

from __future__ import annotations

from dataclasses import dataclass

from config import get_settings
from election_state.control_plane import ElectionControlPlane, ElectionControlSnapshot
from services.audit_service import WORMLogger
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider
from services.voting_service.models.ballot import Ballot, BallotContest
from services.voting_service.models.election_state import ElectionState
from services.voting_service.services.ballot_service import BallotService
from services.voting_service.services.device_revocation_service import DeviceRevocationService
from services.voting_service.services.device_signing import DeviceSigningService
from services.voting_service.services.election_state_manager import ElectionStateManager
from services.voting_service.services.emergency_freeze_service import EmergencyFreezeService
from services.voting_service.services.encryption_service import EncryptionService
from services.voting_service.services.rate_limit_enforcer import RateLimitEnforcer
from services.voting_service.services.result_hash_publisher import ResultHashPublisher
from services.voting_service.services.time_sync_validator import TimeSyncValidator
from services.voting_service.services.token_consumer import TokenConsumer
from services.voting_service.services.token_replay_detector import TokenReplayDetector
from services.voting_service.services.verification_gateway import VerificationGateway
from services.voting_service.services.vote_repository import VoteRepository


@dataclass(frozen=True)
class VotingServiceDependencies:
    """Runtime dependency bundle for vote-casting flows."""

    audit_logger: WORMLogger
    verification_gateway: VerificationGateway
    ballot_service: BallotService
    election_state_manager: ElectionStateManager
    emergency_freeze_service: EmergencyFreezeService
    token_consumer: TokenConsumer
    replay_detector: TokenReplayDetector
    rate_limit_enforcer: RateLimitEnforcer
    time_sync_validator: TimeSyncValidator
    device_revocation_service: DeviceRevocationService
    device_signing_service: DeviceSigningService
    encryption_service: EncryptionService
    result_hash_publisher: ResultHashPublisher
    vote_repository: VoteRepository
    crypto_provider: Phase1CryptoProvider
    control_plane: ElectionControlPlane


def build_voting_dependencies() -> VotingServiceDependencies:
    """Build the default voting-service dependency graph from central settings."""

    settings = get_settings()
    voting_settings = settings.voting_service
    audit_settings = settings.audit_service
    default_ballot = Ballot(
        ballot_id="ballot-2026",
        election_id="election-2026",
        contests=(
            BallotContest(
                contest_id="president",
                prompt="Select one presidential candidate",
                candidates=("candidate-a", "candidate-b", "candidate-c"),
            ),
        ),
    )
    default_election_state = ElectionState("election-2026", "voting", False)
    if voting_settings.use_durable_token_registry:
        token_consumer = TokenConsumer.with_sqlite_store(voting_settings.used_token_registry_path)
        replay_detector = TokenReplayDetector.with_sqlite_store(voting_settings.token_replay_registry_path)
    else:
        token_consumer = TokenConsumer()
        replay_detector = TokenReplayDetector()
    if audit_settings.use_durable_worm_log:
        audit_logger = WORMLogger.with_sqlite_store(audit_settings.worm_log_path)
    else:
        audit_logger = WORMLogger()
    if voting_settings.use_durable_result_publications:
        result_hash_publisher = ResultHashPublisher.with_sqlite_store(voting_settings.result_publication_path)
    else:
        result_hash_publisher = ResultHashPublisher()
    if voting_settings.use_durable_ballot_registry:
        ballot_service = BallotService.with_sqlite_store(voting_settings.ballot_registry_path, ballots=[default_ballot])
    else:
        ballot_service = BallotService(ballots=[default_ballot])
    if voting_settings.use_durable_election_state:
        election_state_manager = ElectionStateManager.with_sqlite_store(
            voting_settings.election_state_path,
            initial_state=default_election_state,
        )
    else:
        election_state_manager = ElectionStateManager(default_election_state)
    if voting_settings.use_durable_device_revocation_registry:
        device_revocation_service = DeviceRevocationService.with_sqlite_store(voting_settings.device_revocation_path)
    else:
        device_revocation_service = DeviceRevocationService()
    if voting_settings.use_durable_emergency_freeze_history:
        emergency_freeze_service = EmergencyFreezeService.with_sqlite_store(
            voting_settings.emergency_freeze_history_path,
            audit_logger=audit_logger,
        )
    else:
        emergency_freeze_service = EmergencyFreezeService(audit_logger=audit_logger)
    if voting_settings.use_durable_rate_limits:
        rate_limit_enforcer = RateLimitEnforcer.with_sqlite_store(
            voting_settings.rate_limit_path,
            per_token_per_minute=settings.rate_limit.per_token_per_minute,
            per_device_per_minute=settings.rate_limit.per_device_per_minute,
        )
    else:
        rate_limit_enforcer = RateLimitEnforcer(
            per_token_per_minute=settings.rate_limit.per_token_per_minute,
            per_device_per_minute=settings.rate_limit.per_device_per_minute,
        )
    if voting_settings.use_durable_vote_repository:
        vote_repository = VoteRepository.with_sqlite_store(voting_settings.vote_repository_path)
    else:
        vote_repository = VoteRepository()
    control_plane_initial_state = ElectionControlSnapshot(
        election_id=default_election_state.election_id,
        phase=election_state_manager.state.phase,
        freeze_active=election_state_manager.state.freeze_active,
        freeze_reason="",
    )
    if voting_settings.use_durable_control_plane:
        control_plane = ElectionControlPlane.with_sqlite_store(
            voting_settings.control_plane_path,
            initial_state=control_plane_initial_state,
            audit_logger=audit_logger,
            phase_audit_path=voting_settings.control_plane_phase_audit_path,
        )
    else:
        control_plane = ElectionControlPlane(
            initial_state=control_plane_initial_state,
            audit_logger=audit_logger,
        )

    return VotingServiceDependencies(
        audit_logger=audit_logger,
        verification_gateway=VerificationGateway(),
        ballot_service=ballot_service,
        election_state_manager=election_state_manager,
        emergency_freeze_service=emergency_freeze_service,
        token_consumer=token_consumer,
        replay_detector=replay_detector,
        rate_limit_enforcer=rate_limit_enforcer,
        time_sync_validator=TimeSyncValidator(),
        device_revocation_service=device_revocation_service,
        device_signing_service=DeviceSigningService(),
        encryption_service=EncryptionService(),
        result_hash_publisher=result_hash_publisher,
        vote_repository=vote_repository,
        crypto_provider=Phase1CryptoProvider(),
        control_plane=control_plane,
    )
