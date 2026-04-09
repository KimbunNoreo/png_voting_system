from __future__ import annotations

from datetime import datetime, timezone
import unittest

from services.nid_client.cache.token_cache import TokenCache
from services.nid_client.client import NIDClient
from services.nid_client.exceptions import NIDClientError, NIDEligibilityError
from services.nid_client.models import VerificationRequest


class _StubTokenValidator:
    def __init__(self, claims: dict[str, object]) -> None:
        self._claims = claims

    def validate(self, token: str) -> dict[str, object]:
        return dict(self._claims)


class TokenCacheTests(unittest.TestCase):
    def test_set_and_get(self) -> None:
        cache = TokenCache(ttl_seconds=30)
        cache.set("k", "v")
        self.assertEqual(cache.get("k"), "v")


class NIDClientClaimPolicyTests(unittest.TestCase):
    def test_validate_token_returns_only_safe_claims(self) -> None:
        client = NIDClient()
        client.token_validator = _StubTokenValidator(
            {
                "jti": "token-1",
                "exp": 9999999999,
                "iat": 1111111111,
                "nbf": 1111111111,
                "sub": "citizen-22",
                "name": "Sensitive Name",
                "eligible": True,
            }
        )
        claims = client.validate_token("token-1")
        self.assertEqual(
            claims,
            {
                "jti": "token-1",
                "exp": 9999999999,
                "iat": 1111111111,
                "nbf": 1111111111,
            },
        )

    def test_validate_token_rejects_claims_without_jti(self) -> None:
        client = NIDClient()
        client.token_validator = _StubTokenValidator({"exp": 9999999999, "iat": 1111111111})
        with self.assertRaises(NIDEligibilityError):
            client.validate_token("token-1")


class NIDClientResponseValidationTests(unittest.TestCase):
    def test_verify_user_rejects_invalid_expiry_format(self) -> None:
        client = NIDClient()
        client._request = lambda *_args, **_kwargs: {  # type: ignore[method-assign]
            "verification_token": "vt-1",
            "token_id": "token-1",
            "eligible": True,
            "expires_at": "not-a-date",
            "signature_kid": "kid-1",
        }
        with self.assertRaises(NIDClientError):
            client.verify_user(
                VerificationRequest(
                    citizen_reference="citizen-ref-1",
                    biometric_assertion="assertion",
                    device_id="device-1",
                    election_id="election-1",
                )
            )

    def test_check_eligibility_rejects_non_boolean_eligible_field(self) -> None:
        client = NIDClient()
        client.validate_token = lambda _token: {"jti": "token-1"}  # type: ignore[method-assign]
        client._request = lambda *_args, **_kwargs: {"eligible": "yes"}  # type: ignore[method-assign]
        with self.assertRaises(NIDClientError):
            client.check_eligibility("token-1")

    def test_verify_user_accepts_valid_schema(self) -> None:
        client = NIDClient()
        now = datetime.now(timezone.utc).replace(microsecond=0)
        client._request = lambda *_args, **_kwargs: {  # type: ignore[method-assign]
            "verification_token": "vt-1",
            "token_id": "token-1",
            "eligible": True,
            "expires_at": now.isoformat(),
            "signature_kid": "kid-1",
        }
        response = client.verify_user(
            VerificationRequest(
                citizen_reference="citizen-ref-1",
                biometric_assertion="assertion",
                device_id="device-1",
                election_id="election-1",
            )
        )
        self.assertEqual(response.token_id, "token-1")
        self.assertTrue(response.eligible)


if __name__ == "__main__":
    unittest.main()
