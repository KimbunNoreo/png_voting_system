from __future__ import annotations

import time
import unittest

import jwt

from services.nid_client.token_validator import TokenValidator

TEST_JWT_HS256_KEY = "phase1-test-hs256-signing-key-material-32b"


class NIDTokenValidationTests(unittest.TestCase):
    def test_token_with_required_claims_decodes_in_untrusted_mode(self) -> None:
        token = jwt.encode(
            {"jti": "1", "iat": int(time.time()), "exp": int(time.time()) + 60},
            TEST_JWT_HS256_KEY,
            algorithm="HS256",
        )
        validator = TokenValidator()
        claims = validator.validate(token)
        self.assertEqual(claims["jti"], "1")


if __name__ == "__main__":
    unittest.main()
