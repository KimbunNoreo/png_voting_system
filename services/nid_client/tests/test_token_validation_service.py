from __future__ import annotations

import unittest

from services.nid_client.token_validation_service import validate_token


class _StubClient:
    def validate_token(self, token: str) -> dict[str, object]:
        return {"jti": f"validated:{token}"}


class TokenValidationServiceTests(unittest.TestCase):
    def test_validate_token_facade_delegates_to_client(self) -> None:
        claims = validate_token("token-1", client=_StubClient())  # type: ignore[arg-type]
        self.assertEqual(claims["jti"], "validated:token-1")


if __name__ == "__main__":
    unittest.main()
