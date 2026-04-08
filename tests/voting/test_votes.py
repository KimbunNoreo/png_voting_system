from __future__ import annotations

from datetime import datetime, timezone
import unittest

from services.audit_service import WORMLogger
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
        return {"jti": "vote-token-1", "eligible": True}

    def check_eligibility(self, token: str) -> bool:
        return True


class VoteFlowTests(unittest.TestCase):
    def test_cast_vote_generates_encrypted_vote(self) -> None:
        crypto = Phase1StandardCrypto()
        device_private = crypto.generate_rsa_private_key()
        tally_private = crypto.generate_rsa_private_key()
        audit_logger = WORMLogger()
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
            token="token-1",
            ballot_id="ballot-1",
            election_id="e1",
            selections={"president": "candidate-a"},
            device_id="device-1",
            device_private_key_pem=crypto.serialize_private_key(device_private),
            tally_public_key_pem=crypto.serialize_public_key(tally_private.public_key()),
            device_time=datetime.now(timezone.utc),
            trusted_time=datetime.now(timezone.utc),
            audit_logger=audit_logger,
        )
        self.assertEqual(vote.election_id, "e1")
        self.assertTrue(vote.encrypted_vote)
        self.assertEqual(audit_logger.entries()[-1].event_type, "vote_cast")
        self.assertEqual(audit_logger.entries()[-1].payload["vote_id"], vote.vote_id)


if __name__ == "__main__":
    unittest.main()
