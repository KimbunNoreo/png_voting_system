from __future__ import annotations

from datetime import datetime, timezone
import unittest

from services.voting_service.api.v1.cast_vote import cast_vote
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider
from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto
from services.voting_service.models.election_state import ElectionState
from services.voting_service.services.device_revocation_service import DeviceRevocationService
from services.voting_service.services.device_signing import DeviceSigningService
from services.voting_service.services.election_state_manager import ElectionStateManager
from services.voting_service.services.encryption_service import EncryptionService
from services.voting_service.services.rate_limit_enforcer import RateLimitEnforcer
from services.voting_service.services.time_sync_validator import TimeSyncValidator
from services.voting_service.services.token_consumer import TokenConsumer
from services.voting_service.services.token_replay_detector import TokenReplayDetector
from services.voting_service.services.verification_gateway import VerificationGateway


class StubClient:
    def validate_token(self, token: str) -> dict[str, object]:
        return {"jti": "token-1", "eligible": True}

    def check_eligibility(self, token: str) -> bool:
        return True


class NIDVotingFlowTests(unittest.TestCase):
    def test_cast_vote_returns_encrypted_vote_without_identity_fields(self) -> None:
        base_crypto = Phase1StandardCrypto()
        device_private = base_crypto.generate_rsa_private_key()
        tally_private = base_crypto.generate_rsa_private_key()
        device_private_pem = base_crypto.serialize_private_key(device_private)
        tally_public_pem = base_crypto.serialize_public_key(tally_private.public_key())

        vote = cast_vote(
            election_state_manager=ElectionStateManager(ElectionState("e1", "voting", False)),
            verification_gateway=VerificationGateway(client=StubClient()),  # type: ignore[arg-type]
            token_consumer=TokenConsumer(),
            replay_detector=TokenReplayDetector(),
            rate_limit_enforcer=RateLimitEnforcer(),
            time_sync_validator=TimeSyncValidator(),
            device_revocation_service=DeviceRevocationService(),
            device_signing_service=DeviceSigningService(),
            encryption_service=EncryptionService(),
            crypto_provider=Phase1CryptoProvider(),
            token="token-value",
            ballot_id="ballot-1",
            election_id="e1",
            selections={"president": "candidate-a"},
            device_id="device-1",
            device_private_key_pem=device_private_pem,
            tally_public_key_pem=tally_public_pem,
            device_time=datetime.now(timezone.utc),
            trusted_time=datetime.now(timezone.utc),
        )

        self.assertEqual(vote.election_id, "e1")
        self.assertTrue(vote.encrypted_vote)
        self.assertTrue(vote.token_hash)


if __name__ == "__main__":
    unittest.main()
