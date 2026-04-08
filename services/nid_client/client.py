"""External NID client with retry, mTLS, caching, and circuit breaking."""

from __future__ import annotations

from datetime import datetime
import time
from typing import Any

import httpx

from config import get_settings
from services.nid_client.authentication import build_httpx_kwargs
from services.nid_client.cache import EligibilityCache, TokenCache
from services.nid_client.circuit_breaker import CircuitBreaker, KBAMultiPersonFallback
from services.nid_client.constants import ENROLL_ENDPOINT, LOOKUP_ENDPOINT, VERIFY_ENDPOINT
from services.nid_client.exceptions import NIDAuthenticationError, NIDClientError, NIDEligibilityError
from services.nid_client.metrics import NIDClientMetrics
from services.nid_client.models import EnrollmentRequest, VerificationRequest, VerificationResponse
from services.nid_client.retry import RetryPolicy, exponential_backoff
from services.nid_client.token_validator import TokenValidator


class NIDClient:
    """Zero-trust client for the external national identity system."""

    def __init__(self) -> None:
        settings = get_settings()
        self.config = settings.nid_integration
        self.retry_policy = RetryPolicy()
        self.breaker = CircuitBreaker()
        self.fallback = KBAMultiPersonFallback()
        self.token_cache = TokenCache()
        self.eligibility_cache = EligibilityCache()
        self.metrics = NIDClientMetrics()
        self.token_validator = TokenValidator()
        self._http_options = build_httpx_kwargs(self.config)

    def _request(self, method: str, path: str, *, json_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        self.breaker.before_request()
        last_error: Exception | None = None
        for attempt in range(1, self.retry_policy.attempts + 1):
            try:
                with httpx.Client(base_url=self.config.base_url, timeout=10.0, **self._http_options) as client:
                    response = client.request(method, path, json=json_payload)
                if response.status_code in (401, 403):
                    raise NIDAuthenticationError("NID authentication failed")
                if response.status_code >= 400:
                    raise NIDClientError(f"NID request failed with {response.status_code}: {response.text}")
                self.breaker.record_success()
                return response.json()
            except Exception as exc:
                self.breaker.record_failure()
                self.metrics.record_error()
                last_error = exc
                if attempt == self.retry_policy.attempts:
                    break
                time.sleep(exponential_backoff(self.retry_policy.base_backoff_seconds, attempt))
        assert last_error is not None
        raise last_error

    def verify_user(self, request: VerificationRequest) -> VerificationResponse:
        cache_key = f"verify:{request.citizen_reference}:{request.election_id}:{request.device_id}"
        cached = self.token_cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        payload = self._request("POST", VERIFY_ENDPOINT, json_payload=request.to_payload())
        self.metrics.record_verify()
        response = VerificationResponse(
            verification_token=payload["verification_token"],
            token_id=payload["token_id"],
            eligible=bool(payload["eligible"]),
            expires_at=datetime.fromisoformat(payload["expires_at"]),
            signature_kid=payload["signature_kid"],
        )
        self.token_cache.set(cache_key, response)
        return response

    def validate_token(self, token: str) -> dict[str, Any]:
        return self.token_validator.validate(token)

    def check_eligibility(self, token: str) -> bool:
        cached = self.eligibility_cache.get(token)
        if cached is not None:
            return bool(cached)
        claims = self.validate_token(token)
        jti = claims.get("jti")
        if not jti:
            raise NIDEligibilityError("NID token missing jti")
        payload = self._request("GET", f"{LOOKUP_ENDPOINT}/{jti}")
        self.metrics.record_lookup()
        eligible = bool(payload.get("eligible", False))
        self.eligibility_cache.set(token, eligible)
        return eligible

    def enroll_user(self, request: EnrollmentRequest) -> dict[str, Any]:
        self.metrics.record_enroll()
        return self._request("POST", ENROLL_ENDPOINT, json_payload=request.to_payload())