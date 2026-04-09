"""Scope-aware sliding window rate limiting for the API gateway."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
import time
from typing import Protocol
from uuid import uuid4

from redis import Redis

from config import get_settings
from services.api_gateway.settings.gateway_settings import GatewaySettings


class SlidingWindowStore(Protocol):
    """Storage abstraction for gateway rate-limiting counters."""

    def add_and_count(self, key: str, now: datetime, window_seconds: int) -> int:
        """Persist a hit for ``key`` and return the number of hits in the active window."""


class InMemorySlidingWindowStore:
    """Local sliding-window store used in tests and single-process development."""

    def __init__(self) -> None:
        self._windows: dict[str, deque[datetime]] = defaultdict(deque)

    def add_and_count(self, key: str, now: datetime, window_seconds: int) -> int:
        window = self._windows[key]
        cutoff = now - timedelta(seconds=window_seconds)
        while window and window[0] <= cutoff:
            window.popleft()
        window.append(now)
        return len(window)


class RedisSlidingWindowStore:
    """Redis-backed sliding-window store for multi-process gateway deployments."""

    def __init__(self, redis_client: Redis) -> None:
        self.redis_client = redis_client

    @classmethod
    def from_settings(cls) -> RedisSlidingWindowStore:
        settings = get_settings()
        return cls(Redis.from_url(settings.cache.location, decode_responses=False))

    def add_and_count(self, key: str, now: datetime, window_seconds: int) -> int:
        now_ms = int(now.timestamp() * 1000)
        cutoff_ms = now_ms - (window_seconds * 1000)
        member = f"{now_ms}:{time.monotonic_ns()}:{uuid4().hex}"
        pipeline = self.redis_client.pipeline()
        pipeline.zremrangebyscore(key, 0, cutoff_ms)
        pipeline.zadd(key, {member: now_ms})
        pipeline.zcard(key)
        pipeline.expire(key, window_seconds)
        _, _, count, _ = pipeline.execute()
        return int(count)


class SlidingWindowRateLimiter:
    """Enforce zero-trust gateway limits without storing raw bearer tokens."""

    def __init__(
        self,
        *,
        settings: GatewaySettings | None = None,
        store: SlidingWindowStore | None = None,
    ) -> None:
        self.settings = settings or GatewaySettings()
        self.window_seconds = self.settings.rate_limit_window_seconds
        self.store = store or self._build_default_store()

    def _build_default_store(self) -> SlidingWindowStore:
        if self.settings.use_redis_rate_limiter:
            return RedisSlidingWindowStore.from_settings()
        return InMemorySlidingWindowStore()

    def _limits_for_bucket(self, bucket: str) -> dict[str, int]:
        base_limits = {
            "ip": self.settings.default_requests_per_minute,
            "client": self.settings.default_requests_per_minute,
        }
        if bucket == "nid":
            return {
                **base_limits,
                "ip": self.settings.nid_requests_per_minute,
                "client": self.settings.nid_requests_per_minute,
            }
        if bucket == "vote":
            return {
                **base_limits,
                "ip": self.settings.vote_requests_per_minute,
                "token": self.settings.vote_token_requests_per_minute,
                "device": self.settings.vote_device_requests_per_minute,
            }
        if bucket == "vote_public":
            return {
                **base_limits,
                "ip": self.settings.vote_public_requests_per_minute,
            }
        return base_limits

    def _build_scopes(self, request: dict[str, object]) -> list[tuple[str, str]]:
        bucket = str(request.get("route_bucket", "default"))
        scopes: list[tuple[str, str]] = []
        ip_address = str(request.get("ip", "")).strip()
        if ip_address:
            scopes.append(("ip", ip_address))

        client_id = str(request.get("client_id", "")).strip()
        if client_id:
            scopes.append(("client", client_id))

        auth_context = request.get("auth_context")
        if isinstance(auth_context, dict):
            token_id = str(auth_context.get("token_id", "")).strip()
            if token_id:
                scopes.append(("token", token_id))

        if bucket == "vote":
            headers = request.get("headers", {})
            device_id = ""
            if isinstance(headers, dict):
                device_id = str(headers.get("X-Device-ID", "")).strip()
            if not device_id:
                device_id = str(request.get("device_id", "")).strip()
            if device_id:
                scopes.append(("device", device_id))
        return scopes

    def enforce(self, request: dict[str, object]) -> None:
        bucket = str(request.get("route_bucket", "default"))
        limits = self._limits_for_bucket(bucket)
        scopes = self._build_scopes(request)
        now = datetime.now(timezone.utc)

        for scope_name, identifier in scopes:
            limit = limits.get(scope_name)
            if limit is None:
                continue
            counter_key = f"gateway:{bucket}:{scope_name}:{identifier}"
            usage = self.store.add_and_count(counter_key, now, self.window_seconds)
            if usage > limit:
                raise ValueError(f"Gateway {scope_name} rate limit exceeded")
