from __future__ import annotations

from datetime import datetime, timezone
import unittest

from services.voting_service.api.v1.cast_vote import cast_vote
from services.voting_service.api.v1.emergency_freeze import activate_freeze
from services.voting_service.api.v1.get_ballot import get_ballot
from services.voting_service.api.v1.observer_tally import observer_tally
from services.voting_service.api.v1.public_result import public_result
from services.voting_service.api.v1.verify_token import verify_token
from services.voting_service.models.election_state import ElectionState
from services.voting_service.models.result_publication import ResultPublication


class _StubGateway:
    def validate_voting_token(self, token: str) -> dict[str, object]:
        return {"jti": "token-1"}


class _NeverCalledBallotService:
    def get(self, ballot_id: str):  # pragma: no cover - this should never run in these tests
        raise AssertionError("Ballot service should not be called for invalid ballot id")


class VotingAPIInputValidationTests(unittest.TestCase):
    def test_verify_token_rejects_blank_token(self) -> None:
        with self.assertRaises(ValueError):
            verify_token("   ", gateway=_StubGateway())  # type: ignore[arg-type]

    def test_get_ballot_rejects_blank_ballot_id(self) -> None:
        with self.assertRaises(ValueError):
            get_ballot(" ", ballot_service=_NeverCalledBallotService())  # type: ignore[arg-type]

    def test_observer_tally_rejects_negative_counts(self) -> None:
        with self.assertRaises(ValueError):
            observer_tally("observer", {"candidate-a": -1})

    def test_observer_tally_rejects_non_integer_counts(self) -> None:
        with self.assertRaises(ValueError):
            observer_tally("observer", {"candidate-a": "5"})  # type: ignore[dict-item]

    def test_public_result_rejects_blank_hash(self) -> None:
        publication = ResultPublication(
            election_id="election-1",
            result_hash=" ",
            published_at=datetime.now(timezone.utc),
        )
        with self.assertRaises(ValueError):
            public_result(publication)

    def test_activate_freeze_rejects_more_than_five_approvals(self) -> None:
        with self.assertRaises(ValueError):
            activate_freeze(ElectionState("e1", "voting", False), "incident", 6)

    def test_activate_freeze_rejects_blank_reason(self) -> None:
        with self.assertRaises(ValueError):
            activate_freeze(ElectionState("e1", "voting", False), " ", 3)

    def test_cast_vote_rejects_empty_selections(self) -> None:
        with self.assertRaises(ValueError):
            cast_vote(
                election_state_manager=None,  # type: ignore[arg-type]
                verification_gateway=None,  # type: ignore[arg-type]
                token_consumer=None,  # type: ignore[arg-type]
                replay_detector=None,  # type: ignore[arg-type]
                rate_limit_enforcer=None,  # type: ignore[arg-type]
                time_sync_validator=None,  # type: ignore[arg-type]
                device_revocation_service=None,  # type: ignore[arg-type]
                device_signing_service=None,  # type: ignore[arg-type]
                encryption_service=None,  # type: ignore[arg-type]
                crypto_provider=None,  # type: ignore[arg-type]
                token="token-1",
                ballot_id="ballot-1",
                election_id="e1",
                selections={},
                device_id="device-1",
                device_private_key_pem="private-pem",
                tally_public_key_pem="public-pem",
                device_time=datetime.now(timezone.utc),
                trusted_time=datetime.now(timezone.utc),
            )

    def test_cast_vote_rejects_non_datetime_device_time(self) -> None:
        with self.assertRaises(ValueError):
            cast_vote(
                election_state_manager=None,  # type: ignore[arg-type]
                verification_gateway=None,  # type: ignore[arg-type]
                token_consumer=None,  # type: ignore[arg-type]
                replay_detector=None,  # type: ignore[arg-type]
                rate_limit_enforcer=None,  # type: ignore[arg-type]
                time_sync_validator=None,  # type: ignore[arg-type]
                device_revocation_service=None,  # type: ignore[arg-type]
                device_signing_service=None,  # type: ignore[arg-type]
                encryption_service=None,  # type: ignore[arg-type]
                crypto_provider=None,  # type: ignore[arg-type]
                token="token-1",
                ballot_id="ballot-1",
                election_id="e1",
                selections={"president": "candidate-a"},
                device_id="device-1",
                device_private_key_pem="private-pem",
                tally_public_key_pem="public-pem",
                device_time="not-a-datetime",  # type: ignore[arg-type]
                trusted_time=datetime.now(timezone.utc),
            )


if __name__ == "__main__":
    unittest.main()
