"""External NID service connection configuration."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class NIDIntegrationConfig:
    base_url: str = os.getenv("NID_BASE_URL", "https://nid.example.gov.pg")
    verify_path: str = "/api/v1/verify"
    lookup_path: str = "/api/v1/eligibility"
    enroll_path: str = "/api/v1/enroll"
    mtls_cert_path: str | None = os.getenv("NID_MTLS_CERT_PATH")
    mtls_key_path: str | None = os.getenv("NID_MTLS_KEY_PATH")
    ca_bundle_path: str | None = os.getenv("NID_CA_BUNDLE_PATH")
    api_key: str | None = os.getenv("NID_API_KEY")