"""Database configuration helpers."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DatabaseConfig:
    engine: str
    name: str
    host: str
    port: int
    user: str
    password: str
    ssl_mode: str
    conn_max_age: int
    statement_timeout_ms: int

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        return cls(
            engine="django.db.backends.postgresql",
            name=os.getenv("DB_NAME", "securevote"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", "securevote"),
            password=os.getenv("DB_PASSWORD", "securevote"),
            ssl_mode=os.getenv("DB_SSLMODE", "require"),
            conn_max_age=int(os.getenv("DB_CONN_MAX_AGE", "60")),
            statement_timeout_ms=int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "5000")),
        )

    def as_django_dict(self) -> dict[str, object]:
        return {
            "default": {
                "ENGINE": self.engine,
                "NAME": self.name,
                "HOST": self.host,
                "PORT": self.port,
                "USER": self.user,
                "PASSWORD": self.password,
                "CONN_MAX_AGE": self.conn_max_age,
                "OPTIONS": {
                    "sslmode": self.ssl_mode,
                    "options": f"-c statement_timeout={self.statement_timeout_ms}",
                },
            }
        }