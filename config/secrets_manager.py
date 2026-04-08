"""Secrets manager abstraction."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class SecretsManagerConfig:
    provider: str = os.getenv("SECRETS_PROVIDER", "environment")
    vault_url: str | None = os.getenv("VAULT_ADDR")
    aws_region: str | None = os.getenv("AWS_REGION")