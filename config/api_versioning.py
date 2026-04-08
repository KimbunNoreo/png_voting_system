"""API versioning configuration."""

from __future__ import annotations

from dataclasses import dataclass

from config.constants import API_V1_PREFIX, API_V2_PREFIX


@dataclass(frozen=True)
class APIVersioningConfig:
    supported_versions: tuple[str, ...] = ("v1", "v2")
    default_prefix: str = API_V1_PREFIX
    future_prefix: str = API_V2_PREFIX