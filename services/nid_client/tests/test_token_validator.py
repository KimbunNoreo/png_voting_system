from __future__ import annotations
import time
import unittest
import jwt
from services.nid_client.token_validator import TokenValidator
class TokenValidatorTests(unittest.TestCase):
    def test_validate_unsigned_claims_when_no_public_key_is_configured(self) -> None:
        token = jwt.encode({"jti": "abc", "iat": int(time.time()), "exp": int(time.time()) + 60}, "secret", algorithm="HS256")
        validator = TokenValidator()
        with self.assertRaises(Exception):
            validator.validate(token)
if __name__ == "__main__":
    unittest.main()