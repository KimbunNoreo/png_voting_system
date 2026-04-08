from __future__ import annotations
import uuid
from services.audit_service import WORMLogger
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider
from services.voting_service.models.vote import Vote
from services.voting_service.services.device_revocation_service import DeviceRevocationService
from services.voting_service.services.device_signing import DeviceSigningService
from services.voting_service.services.election_state_manager import ElectionStateManager
from services.voting_service.services.encryption_service import EncryptionService
from services.voting_service.services.rate_limit_enforcer import RateLimitEnforcer
from services.voting_service.services.time_sync_validator import TimeSyncValidator
from services.voting_service.services.token_consumer import TokenConsumer
from services.voting_service.services.token_replay_detector import TokenReplayDetector
from services.voting_service.services.verification_gateway import VerificationGateway
def cast_vote(*, election_state_manager: ElectionStateManager, verification_gateway: VerificationGateway, token_consumer: TokenConsumer, replay_detector: TokenReplayDetector, rate_limit_enforcer: RateLimitEnforcer, time_sync_validator: TimeSyncValidator, device_revocation_service: DeviceRevocationService, device_signing_service: DeviceSigningService, encryption_service: EncryptionService, crypto_provider: Phase1CryptoProvider, token: str, ballot_id: str, election_id: str, selections: dict[str, object], device_id: str, device_private_key_pem: str, tally_public_key_pem: str, device_time, trusted_time, audit_logger: WORMLogger | None = None) -> Vote:
    election_state_manager.ensure_voting_open(); time_sync_validator.validate(device_time, trusted_time); device_revocation_service.assert_not_revoked(device_id)
    claims = verification_gateway.validate_voting_token(token); token_hash = crypto_provider.hash_token(token); rate_limit_enforcer.check(token_hash, device_id)
    replay_attempt = replay_detector.register(token_hash, device_id)
    if replay_attempt is not None:
        if audit_logger is not None:
            audit_logger.append("vote_replay_detected", {"election_id": election_id, "token_hash": token_hash, "original_device_id": replay_attempt.original_device_id, "replay_device_id": replay_attempt.replay_device_id})
        raise ValueError("Global token replay detected")
    token_consumer.consume(token_hash, device_id)
    payload = {"ballot_id": ballot_id, "election_id": election_id, "selections": selections, "token_jti": claims.get("jti")}
    vote_id = str(uuid.uuid4()); signature = device_signing_service.sign_vote(vote_id, device_id, payload, device_private_key_pem)
    vote = encryption_service.encrypt_vote(vote_id=vote_id, election_id=election_id, ballot_id=ballot_id, selections=payload, device_id=device_id, device_signature=signature.signature, token_hash=token_hash, recipient_public_key_pem=tally_public_key_pem, kid="phase1-default")
    if audit_logger is not None:
        audit_logger.append("vote_cast", {"vote_id": vote.vote_id, "election_id": vote.election_id, "ballot_id": vote.ballot_id, "device_id": vote.device_id, "token_hash": vote.token_hash, "kid": vote.kid})
    return vote
