"""Redis cache configuration."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class CacheConfig:
    backend: str = "django_redis.cache.RedisCache"
    location: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    use_tls: bool = True
    timeout_seconds: int = 300

    def as_django_dict(self) -> dict[str, object]:
        return {
            "default": {
                "BACKEND": self.backend,
                "LOCATION": self.location,
                "TIMEOUT": self.timeout_seconds,
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "SSL": self.use_tls,
                },
            }
        }