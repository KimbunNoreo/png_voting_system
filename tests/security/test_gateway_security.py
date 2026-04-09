from __future__ import annotations

import unittest
from unittest.mock import patch

from services.api_gateway import GatewayApplication
from services.api_gateway.auth_proxy import AuthProxy
from services.api_gateway.middleware.emergency_freeze import EmergencyFreezeMiddleware
from services.api_gateway.middleware.ip_filter import IPFilterMiddleware
from services.api_gateway.middleware.mTLS_verifier import MTLSVerifierMiddleware
from services.api_gateway.settings.gateway_settings import GatewaySettings
from services.api_gateway.settings.security_settings import GatewaySecuritySettings
from services.api_gateway.rate_limit import (
    InMemorySlidingWindowStore,
    RedisSlidingWindowStore,
    SlidingWindowRateLimiter,
)
from services.api_gateway.routing import GatewayRouter


class StubTokenValidator:
    def __init__(self, *, claims: dict[str, object] | None = None, error: Exception | None = None) -> None:
        self.claims = claims or {"jti": "token-123", "exp": 9999999999, "iat": 1111111111}
        self.error = error

    def validate(self, token: str) -> dict[str, object]:
        if self.error is not None:
            raise self.error
        return dict(self.claims)


def build_client_certificate(
    *,
    subject: str = "CN=voting-service.internal,O=SecureVote PNG,C=PG",
    spiffe_id: str = "spiffe://securevote/internal/voting-service",
    chain_verified: bool = True,
    client_auth: bool = True,
    not_before: str = "2026-01-01T00:00:00+00:00",
    not_after: str = "2027-01-01T00:00:00+00:00",
) -> dict[str, object]:
    return {
        "subject": subject,
        "spiffe_id": spiffe_id,
        "chain_verified": chain_verified,
        "client_auth": client_auth,
        "not_before": not_before,
        "not_after": not_after,
    }


class FakeRedisPipeline:
    def __init__(self, redis_client: FakeRedisClient) -> None:
        self.redis_client = redis_client
        self.operations: list[tuple[str, tuple[object, ...]]] = []

    def zremrangebyscore(self, key: str, minimum: int, maximum: int) -> FakeRedisPipeline:
        self.operations.append(("zremrangebyscore", (key, minimum, maximum)))
        return self

    def zadd(self, key: str, mapping: dict[str, int]) -> FakeRedisPipeline:
        self.operations.append(("zadd", (key, mapping)))
        return self

    def zcard(self, key: str) -> FakeRedisPipeline:
        self.operations.append(("zcard", (key,)))
        return self

    def expire(self, key: str, seconds: int) -> FakeRedisPipeline:
        self.operations.append(("expire", (key, seconds)))
        return self

    def execute(self) -> list[object]:
        results: list[object] = []
        for operation, args in self.operations:
            handler = getattr(self.redis_client, f"_handle_{operation}")
            results.append(handler(*args))
        self.operations.clear()
        return results


class FakeRedisClient:
    def __init__(self) -> None:
        self.sorted_sets: dict[str, dict[str, int]] = {}
        self.expiry: dict[str, int] = {}

    def pipeline(self) -> FakeRedisPipeline:
        return FakeRedisPipeline(self)

    def _handle_zremrangebyscore(self, key: str, minimum: int, maximum: int) -> int:
        bucket = self.sorted_sets.setdefault(key, {})
        to_remove = [member for member, score in bucket.items() if minimum <= score <= maximum]
        for member in to_remove:
            del bucket[member]
        return len(to_remove)

    def _handle_zadd(self, key: str, mapping: dict[str, int]) -> int:
        bucket = self.sorted_sets.setdefault(key, {})
        before = len(bucket)
        bucket.update(mapping)
        return len(bucket) - before

    def _handle_zcard(self, key: str) -> int:
        return len(self.sorted_sets.setdefault(key, {}))

    def _handle_expire(self, key: str, seconds: int) -> bool:
        self.expiry[key] = seconds
        return True


class GatewaySecurityTests(unittest.TestCase):
    def test_tls_is_required(self) -> None:
        app = GatewayApplication(router=GatewayRouter(), auth_proxy=AuthProxy(token_validator=StubTokenValidator()))
        with self.assertRaises(PermissionError):
            app.handle_request(
                {
                    "path": "/api/v1/vote/cast",
                    "headers": {"Authorization": "Bearer token"},
                    "is_tls": False,
                    "client_certificate_verified": True,
                    "client_certificate": build_client_certificate(),
                    "ip": "127.0.0.1",
                    "body": "{}",
                }
            )

    def test_emergency_freeze_blocks_vote_requests(self) -> None:
        app = GatewayApplication(
            router=GatewayRouter(),
            auth_proxy=AuthProxy(token_validator=StubTokenValidator()),
            emergency_freeze=EmergencyFreezeMiddleware(frozen=True),
        )
        with self.assertRaises(PermissionError):
            app.handle_request(
                {
                    "path": "/api/v1/vote/cast",
                    "headers": {"Authorization": "Bearer token"},
                    "is_tls": True,
                    "client_certificate_verified": True,
                    "client_certificate": build_client_certificate(),
                    "ip": "127.0.0.1",
                    "body": "{}",
                }
            )

    def test_vote_routes_require_bearer_token_format(self) -> None:
        app = GatewayApplication(router=GatewayRouter())
        with self.assertRaises(PermissionError):
            app.handle_request(
                {
                    "path": "/api/v1/vote/cast",
                    "headers": {"Authorization": "token-without-bearer-prefix"},
                    "is_tls": True,
                    "client_certificate_verified": True,
                    "client_certificate": build_client_certificate(),
                    "ip": "127.0.0.1",
                    "body": "{}",
                }
            )

    def test_vote_token_rate_limit_is_enforced(self) -> None:
        app = GatewayApplication(
            router=GatewayRouter(),
            auth_proxy=AuthProxy(token_validator=StubTokenValidator()),
            rate_limiter=SlidingWindowRateLimiter(
                store=InMemorySlidingWindowStore(),
            ),
        )
        request = {
            "path": "/api/v1/vote/cast",
            "headers": {
                "Authorization": "Bearer valid-token",
                "X-Device-ID": "device-1",
            },
            "is_tls": True,
            "client_certificate_verified": True,
            "client_certificate": build_client_certificate(),
            "ip": "127.0.0.1",
            "body": "{}",
        }
        result = app.handle_request(request)
        self.assertEqual(result["request"]["auth_context"]["token_id"], "token-123")

        strict_app = GatewayApplication(
            router=GatewayRouter(),
            auth_proxy=AuthProxy(token_validator=StubTokenValidator()),
            rate_limiter=SlidingWindowRateLimiter(
                settings=GatewaySettings(
                    vote_token_requests_per_minute=1,
                    vote_device_requests_per_minute=10,
                    vote_requests_per_minute=10,
                ),
                store=InMemorySlidingWindowStore(),
            ),
        )
        strict_app.handle_request(dict(request))
        with self.assertRaises(ValueError):
            strict_app.handle_request(dict(request))

    def test_gateway_rejects_untrusted_client_certificate(self) -> None:
        app = GatewayApplication(
            router=GatewayRouter(),
            auth_proxy=AuthProxy(token_validator=StubTokenValidator()),
            mtls_verifier=MTLSVerifierMiddleware(
                security_settings=GatewaySecuritySettings(
                    trusted_client_certificate_subjects=("CN=voting-service.internal,O=SecureVote PNG,C=PG",),
                    trusted_client_spiffe_ids=("spiffe://securevote/internal/voting-service",),
                )
            ),
        )
        with self.assertRaises(PermissionError):
            app.handle_request(
                {
                    "path": "/api/v1/vote/cast",
                    "headers": {"Authorization": "Bearer token"},
                    "is_tls": True,
                    "client_certificate_verified": True,
                    "client_certificate": build_client_certificate(
                        subject="CN=rogue-service.internal,O=Unknown,C=PG",
                        spiffe_id="spiffe://rogue/internal/service",
                    ),
                    "ip": "127.0.0.1",
                    "body": "{}",
                }
            )

    def test_gateway_rejects_ip_outside_allowlist(self) -> None:
        app = GatewayApplication(
            router=GatewayRouter(),
            auth_proxy=AuthProxy(token_validator=StubTokenValidator()),
            ip_filter=IPFilterMiddleware(
                security_settings=GatewaySecuritySettings(allowed_cidrs=("127.0.0.1/32",))
            ),
        )
        with self.assertRaises(PermissionError):
            app.handle_request(
                {
                    "path": "/api/v1/nid/verify",
                    "headers": {},
                    "is_tls": True,
                    "client_certificate_verified": True,
                    "client_certificate": build_client_certificate(
                        subject="CN=nid-client.internal,O=SecureVote PNG,C=PG",
                        spiffe_id="spiffe://securevote/internal/nid-client",
                    ),
                    "ip": "10.10.10.10",
                    "body": "{}",
                }
            )

    def test_redis_sliding_window_store_counts_requests(self) -> None:
        redis_client = FakeRedisClient()
        store = RedisSlidingWindowStore(redis_client=redis_client)
        limiter = SlidingWindowRateLimiter(
            settings=GatewaySettings(vote_token_requests_per_minute=1, use_redis_rate_limiter=True),
            store=store,
        )
        request = {
            "route_bucket": "vote",
            "ip": "127.0.0.1",
            "client_id": "token:token-123",
            "auth_context": {"token_id": "token-123", "claims": {"jti": "token-123"}},
            "headers": {"X-Device-ID": "device-1"},
        }
        limiter.enforce(dict(request))
        with self.assertRaises(ValueError):
            limiter.enforce(dict(request))
        self.assertTrue(any(key.startswith("gateway:vote:token:token-123") for key in redis_client.sorted_sets))

    def test_rate_limiter_selects_redis_store_when_enabled(self) -> None:
        fake_store = RedisSlidingWindowStore(redis_client=FakeRedisClient())
        with patch(
            "services.api_gateway.rate_limit.RedisSlidingWindowStore.from_settings",
            return_value=fake_store,
        ):
            limiter = SlidingWindowRateLimiter(
                settings=GatewaySettings(use_redis_rate_limiter=True),
            )
        self.assertIs(limiter.store, fake_store)

    def test_gateway_rejects_control_characters_in_headers(self) -> None:
        app = GatewayApplication(router=GatewayRouter())
        with self.assertRaises(ValueError):
            app.handle_request(
                {
                    "path": "/api/v1/nid/verify",
                    "headers": {"X-Test": "clean\r\nInjected: bad"},
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

    def test_gateway_rejects_sql_injection_in_query(self) -> None:
        app = GatewayApplication(router=GatewayRouter())
        with self.assertRaises(ValueError):
            app.handle_request(
                {
                    "path": "/api/v1/nid/verify",
                    "headers": {},
                    "query": {"token": "' OR 1=1 --"},
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

    def test_gateway_rejects_script_payload_in_body(self) -> None:
        app = GatewayApplication(router=GatewayRouter(), auth_proxy=AuthProxy(token_validator=StubTokenValidator()))
        with self.assertRaises(ValueError):
            app.handle_request(
                {
                    "path": "/api/v1/vote/cast",
                    "headers": {"Authorization": "Bearer valid-token"},
                    "is_tls": True,
                    "client_certificate_verified": True,
                    "client_certificate": build_client_certificate(),
                    "ip": "127.0.0.1",
                    "body": "<script>alert('xss')</script>",
                }
            )

    def test_gateway_auth_context_only_keeps_safe_claims(self) -> None:
        app = GatewayApplication(
            router=GatewayRouter(),
            auth_proxy=AuthProxy(
                token_validator=StubTokenValidator(
                    claims={
                        "jti": "vote-token-7",
                        "exp": 9999999999,
                        "iat": 1111111111,
                        "nbf": 1111111111,
                        "sub": "citizen-7",
                        "name": "Sensitive Name",
                        "eligible": True,
                        "biometrics": {"face": "template"},
                    }
                )
            ),
        )
        result = app.handle_request(
            {
                "path": "/api/v1/vote/cast",
                "headers": {"Authorization": "Bearer valid-token"},
                "is_tls": True,
                "client_certificate_verified": True,
                "client_certificate": build_client_certificate(),
                "ip": "127.0.0.1",
                "body": "{}",
            }
        )
        self.assertEqual(
            result["request"]["auth_context"]["claims"],
            {
                "jti": "vote-token-7",
                "exp": 9999999999,
                "iat": 1111111111,
                "nbf": 1111111111,
            },
        )

    def test_public_result_route_rejects_non_get_methods(self) -> None:
        app = GatewayApplication(router=GatewayRouter())
        with self.assertRaises(ValueError):
            app.handle_request(
                {
                    "path": "/api/v1/vote/public-result/election-2026",
                    "method": "POST",
                    "headers": {},
                    "is_tls": True,
                    "client_certificate_verified": True,
                    "client_certificate": build_client_certificate(),
                    "ip": "127.0.0.1",
                    "body": "{}",
                }
            )

    def test_public_result_route_is_rate_limited_by_ip(self) -> None:
        app = GatewayApplication(
            router=GatewayRouter(),
            rate_limiter=SlidingWindowRateLimiter(
                settings=GatewaySettings(vote_public_requests_per_minute=1),
                store=InMemorySlidingWindowStore(),
            ),
        )
        request = {
            "path": "/api/v1/vote/public-result/election-2026",
            "method": "GET",
            "headers": {},
            "is_tls": True,
            "client_certificate_verified": True,
            "client_certificate": build_client_certificate(),
            "ip": "127.0.0.1",
            "body": "{}",
        }
        first = app.handle_request(dict(request))
        self.assertEqual(first["request"]["route_bucket"], "vote_public")
        with self.assertRaises(ValueError):
            app.handle_request(dict(request))


if __name__ == "__main__":
    unittest.main()
