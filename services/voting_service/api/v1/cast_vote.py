from __future__ import annotations

from datetime import datetime
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


def _require_non_empty(value: str, field_name: str) -> str:
    cleaned = str(value).strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def _require_datetime(value: datetime, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise ValueError(f"{field_name} must be a datetime")
    return value


def _validate_selections(selections: dict[str, object]) -> dict[str, object]:
    if not isinstance(selections, dict):
        raise ValueError("selections must be a dictionary")
    if not selections:
        raise ValueError("selections must include at least one choice")
    normalized: dict[str, object] = {}
    for key, value in selections.items():
        normalized_key = str(key).strip()
        if not normalized_key:
            raise ValueError("selection keys must be non-empty")
        if value is None:
            raise ValueError(f"selection '{normalized_key}' cannot be null")
        normalized[normalized_key] = value
    return normalized


def cast_vote(
    *,
    election_state_manager: ElectionStateManager,
    verification_gateway: VerificationGateway,
    token_consumer: TokenConsumer,
    replay_detector: TokenReplayDetector,
    rate_limit_enforcer: RateLimitEnforcer,
    time_sync_validator: TimeSyncValidator,
    device_revocation_service: DeviceRevocationService,
    device_signing_service: DeviceSigningService,
    encryption_service: EncryptionService,
    crypto_provider: Phase1CryptoProvider,
    token: str,
    ballot_id: str,
    election_id: str,
    selections: dict[str, object],
    device_id: str,
    device_private_key_pem: str,
    tally_public_key_pem: str,
    device_time,
    trusted_time,
    audit_logger: WORMLogger | None = None,
) -> Vote:
    token_value = _require_non_empty(token, "token")
    ballot_id_value = _require_non_empty(ballot_id, "ballot_id")
    election_id_value = _require_non_empty(election_id, "election_id")
    device_id_value = _require_non_empty(device_id, "device_id")
    device_private_key_pem_value = _require_non_empty(device_private_key_pem, "device_private_key_pem")
    tally_public_key_pem_value = _require_non_empty(tally_public_key_pem, "tally_public_key_pem")
    normalized_selections = _validate_selections(selections)
    _require_datetime(device_time, "device_time")
    _require_datetime(trusted_time, "trusted_time")

    election_state_manager.ensure_voting_open()
    time_sync_validator.validate(device_time, trusted_time)
    device_revocation_service.assert_not_revoked(device_id_value)

    claims = verification_gateway.validate_voting_token(token_value)
    token_hash = crypto_provider.hash_token(token_value)
    rate_limit_enforcer.check(token_hash, device_id_value)

    replay_attempt = replay_detector.register(token_hash, device_id_value)
    if replay_attempt is not None:
        if audit_logger is not None:
            audit_logger.append(
                "vote_replay_detected",
                {
                    "election_id": election_id_value,
                    "token_hash": token_hash,
                    "original_device_id": replay_attempt.original_device_id,
                    "replay_device_id": replay_attempt.replay_device_id,
                },
            )
        raise ValueError("Global token replay detected")

    token_consumer.consume(token_hash, device_id_value)

    payload = {
        "ballot_id": ballot_id_value,
        "election_id": election_id_value,
        "selections": normalized_selections,
        "token_jti": claims.get("jti"),
    }
    vote_id = str(uuid.uuid4())
    signature = device_signing_service.sign_vote(vote_id, device_id_value, payload, device_private_key_pem_value)

    vote = encryption_service.encrypt_vote(
        vote_id=vote_id,
        election_id=election_id_value,
        ballot_id=ballot_id_value,
        selections=payload,
        device_id=device_id_value,
        device_signature=signature.signature,
        token_hash=token_hash,
        recipient_public_key_pem=tally_public_key_pem_value,
        kid="phase1-default",
    )
    if audit_logger is not None:
        audit_logger.append(
            "vote_cast",
            {
                "vote_id": vote.vote_id,
                "election_id": vote.election_id,
                "ballot_id": vote.ballot_id,
                "device_id": vote.device_id,
                "token_hash": vote.token_hash,
                "kid": vote.kid,
            },
        )
    return vote
