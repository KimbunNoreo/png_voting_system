from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import unittest
from uuid import uuid4

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
        return {"jti": token, "eligible": True}

    def check_eligibility(self, token: str) -> bool:
        return True


class TokenReplayGlobalTests(unittest.TestCase):
    def test_replay_detected_across_devices(self) -> None:
        detector = TokenReplayDetector()
        self.assertIsNone(detector.register("token-hash", "device-1"))
        replay = detector.register("token-hash", "device-2")
        self.assertIsNotNone(replay)
        self.assertEqual(replay.original_device_id, "device-1")

    def test_replay_detector_rejects_blank_identifiers(self) -> None:
        detector = TokenReplayDetector()
        with self.assertRaises(ValueError):
            detector.register(" ", "device-1")
        with self.assertRaises(ValueError):
            detector.register("token-hash", " ")

    def test_replay_detection_survives_restart_with_sqlite_store(self) -> None:
        database_dir = Path("data") / "test_runtime"
        database_dir.mkdir(parents=True, exist_ok=True)
        database_path = database_dir / f"token_replay_{uuid4().hex}.sqlite3"
        try:
            first_detector = TokenReplayDetector.with_sqlite_store(database_path)
            self.assertIsNone(first_detector.register("token-hash", "device-1"))

            second_detector = TokenReplayDetector.with_sqlite_store(database_path)
            replay = second_detector.register("token-hash", "device-2")
            self.assertIsNotNone(replay)
            self.assertEqual(replay.original_device_id, "device-1")
            self.assertEqual(replay.replay_device_id, "device-2")
        finally:
            if database_path.exists():
                database_path.unlink()

    def test_replay_detection_is_audited_when_vote_cast_reused_on_new_device(self) -> None:
        crypto = Phase1StandardCrypto()
        tally_private = crypto.generate_rsa_private_key()
        tally_public_key_pem = crypto.serialize_public_key(tally_private.public_key())
        device_one_private_key = crypto.serialize_private_key(crypto.generate_rsa_private_key())
        device_two_private_key = crypto.serialize_private_key(crypto.generate_rsa_private_key())
        audit_logger = WORMLogger()
        replay_detector = TokenReplayDetector()
        token_consumer = TokenConsumer()

        cast_vote(
            election_state_manager=ElectionStateManager(ElectionState("e1", "voting", False)),
            verification_gateway=VerificationGateway(client=StubClient()),  # type: ignore[arg-type]
            token_consumer=token_consumer,
            replay_detector=replay_detector,
            rate_limit_enforcer=RateLimitEnforcer(),
            time_sync_validator=TimeSyncValidator(),
            device_revocation_service=DeviceRevocationService(),
            device_signing_service=DeviceSigningService(),
            encryption_service=EncryptionService(),
            crypto_provider=Phase1CryptoProvider(),
            token="demo-token",
            ballot_id="ballot-1",
            election_id="e1",
            selections={"president": "candidate-a"},
            device_id="device-1",
            device_private_key_pem=device_one_private_key,
            tally_public_key_pem=tally_public_key_pem,
            device_time=datetime.now(timezone.utc),
            trusted_time=datetime.now(timezone.utc),
            audit_logger=audit_logger,
        )

        with self.assertRaises(ValueError):
            cast_vote(
                election_state_manager=ElectionStateManager(ElectionState("e1", "voting", False)),
                verification_gateway=VerificationGateway(client=StubClient()),  # type: ignore[arg-type]
                token_consumer=token_consumer,
                replay_detector=replay_detector,
                rate_limit_enforcer=RateLimitEnforcer(per_token_per_minute=2, per_device_per_minute=10),
                time_sync_validator=TimeSyncValidator(),
                device_revocation_service=DeviceRevocationService(),
                device_signing_service=DeviceSigningService(),
                encryption_service=EncryptionService(),
                crypto_provider=Phase1CryptoProvider(),
                token="demo-token",
                ballot_id="ballot-1",
                election_id="e1",
                selections={"president": "candidate-a"},
                device_id="device-2",
                device_private_key_pem=device_two_private_key,
                tally_public_key_pem=tally_public_key_pem,
                device_time=datetime.now(timezone.utc),
                trusted_time=datetime.now(timezone.utc),
                audit_logger=audit_logger,
            )

        self.assertEqual(audit_logger.entries()[-1].event_type, "vote_replay_detected")


if __name__ == "__main__":
    unittest.main()
