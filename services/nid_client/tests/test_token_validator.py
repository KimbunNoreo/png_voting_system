from __future__ import annotations
import time
import unittest
import jwt
from services.nid_client.exceptions import NIDValidationError
from services.nid_client.token_validator import TokenValidator

TEST_JWT_HS256_KEY = "phase1-test-hs256-signing-key-material-32b"


class TokenValidatorTests(unittest.TestCase):
    def test_validate_claims_when_no_public_key_is_configured(self) -> None:
        token = jwt.encode(
            {"jti": "abc", "iat": int(time.time()), "exp": int(time.time()) + 60},
            TEST_JWT_HS256_KEY,
            algorithm="HS256",
        )
        validator = TokenValidator()
        claims = validator.validate(token)
        self.assertEqual(claims["jti"], "abc")

    def test_rejects_untrusted_none_algorithm(self) -> None:
        token = jwt.encode(
            {"jti": "abc", "iat": int(time.time()), "exp": int(time.time()) + 60},
            key="",
            algorithm="none",
        )
        validator = TokenValidator()
        with self.assertRaises(NIDValidationError):
            validator.validate(token)
if __name__ == "__main__":
    unittest.main()
