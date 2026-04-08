"""Authentication helpers for secure NID connectivity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config.nid_integration import NIDIntegrationConfig


@dataclass(frozen=True)
class MTLSConfig:
    cert_path: str
    key_path: str
    ca_bundle_path: str | None = None


def build_httpx_kwargs(config: NIDIntegrationConfig) -> dict[str, Any]:
    headers: dict[str, str] = {}
    if config.api_key:
        headers["X-API-Key"] = config.api_key

    kwargs: dict[str, Any] = {"headers": headers}
    if config.ca_bundle_path:
        kwargs["verify"] = config.ca_bundle_path
    if config.mtls_cert_path and config.mtls_key_path:
        kwargs["cert"] = (config.mtls_cert_path, config.mtls_key_path)
    return kwargs