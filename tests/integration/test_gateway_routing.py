from __future__ import annotations

import unittest

from services.api_gateway import GatewayApplication
from services.api_gateway.auth_proxy import AuthProxy
from services.api_gateway.routing import GatewayRouter


class StubTokenValidator:
    def validate(self, token: str) -> dict[str, object]:
        return {
            "jti": "vote-token-1",
            "exp": 9999999999,
            "iat": 1111111111,
            "eligible": True,
            "sub": "citizen-should-not-be-forwarded",
            "name": "Sensitive Name",
        }


def build_client_certificate(
    *,
    subject: str = "CN=voting-service.internal,O=SecureVote PNG,C=PG",
    spiffe_id: str = "spiffe://securevote/internal/voting-service",
) -> dict[str, object]:
    return {
        "subject": subject,
        "spiffe_id": spiffe_id,
        "chain_verified": True,
        "client_auth": True,
        "not_before": "2026-01-01T00:00:00+00:00",
        "not_after": "2027-01-01T00:00:00+00:00",
    }


class GatewayRoutingTests(unittest.TestCase):
    def test_gateway_routes_vote_requests(self) -> None:
        app = GatewayApplication(router=GatewayRouter(), auth_proxy=AuthProxy(token_validator=StubTokenValidator()))
        result = app.handle_request(
            {
                "path": "/api/v1/vote/cast",
                "method": " post ",
                "headers": {"Authorization": "Bearer token"},
                "is_tls": True,
                "client_certificate_verified": True,
                "client_certificate": build_client_certificate(),
                "ip": "127.0.0.1",
                "body": "{}",
            }
        )
        self.assertEqual(result["route"], "voting_service")
        self.assertEqual(result["request"]["auth_context"]["token_id"], "vote-token-1")
        self.assertNotIn("sub", result["request"]["auth_context"]["claims"])
        self.assertNotIn("eligible", result["request"]["auth_context"]["claims"])
        self.assertNotIn("name", result["request"]["auth_context"]["claims"])
        self.assertEqual(result["request"]["method"], "POST")

    def test_gateway_routes_nid_requests(self) -> None:
        app = GatewayApplication(router=GatewayRouter())
        result = app.handle_request(
            {
                "path": "/api/v1/nid/verify",
                "headers": {},
                "is_tls": True,
                "client_certificate_verified": True,
                "client_certificate": build_client_certificate(
                    subject="CN=nid-client.internal,O=SecureVote PNG,C=PG",
                    spiffe_id="spiffe://securevote/internal/nid-client",
                ),
                "ip": "127.0.0.1",
                "body": "{}",
            }
        )
        self.assertEqual(result["route"], "external_nid")

    def test_gateway_normalizes_vote_path_before_routing(self) -> None:
        app = GatewayApplication(router=GatewayRouter(), auth_proxy=AuthProxy(token_validator=StubTokenValidator()))
        result = app.handle_request(
            {
                "path": "//api//v1//vote//cast",
                "headers": {"Authorization": "Bearer token"},
                "is_tls": True,
                "client_certificate_verified": True,
                "client_certificate": build_client_certificate(),
                "ip": "127.0.0.1",
                "body": "{}",
            }
        )
        self.assertEqual(result["route"], "voting_service")

    def test_gateway_sanitizes_query_dictionary(self) -> None:
        app = GatewayApplication(router=GatewayRouter())
        result = app.handle_request(
            {
                "path": "/api/v1/nid/verify",
                "query": {" lookup ": " voter-123 "},
                "headers": {},
                "is_tls": True,
                "client_certificate_verified": True,
                "client_certificate": build_client_certificate(
                    subject="CN=nid-client.internal,O=SecureVote PNG,C=PG",
                    spiffe_id="spiffe://securevote/internal/nid-client",
                ),
                "ip": "127.0.0.1",
                "body": "{}",
            }
        )
        self.assertEqual(result["request"]["query"], {"lookup": "voter-123"})


if __name__ == "__main__":
    unittest.main()
