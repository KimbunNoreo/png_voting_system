"""mTLS verification middleware."""

from __future__ import annotations

from datetime import datetime, timezone

from services.api_gateway.settings.security_settings import GatewaySecuritySettings


class MTLSVerifierMiddleware:
    """Verify client certificate metadata for zero-trust service admission."""

    def __init__(self, security_settings: GatewaySecuritySettings | None = None) -> None:
        self.security_settings = security_settings or GatewaySecuritySettings()

    def _parse_timestamp(self, value: object, field_name: str) -> datetime:
        if not isinstance(value, str) or not value.strip():
            raise PermissionError(f"Client certificate {field_name} is required")
        normalized = value.strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise PermissionError(f"Client certificate {field_name} is invalid") from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    def _verify_certificate(self, certificate: dict[str, object]) -> None:
        if self.security_settings.require_certificate_chain_validation and not certificate.get("chain_verified", False):
            raise PermissionError("mTLS certificate chain verification failed")
        if self.security_settings.require_client_auth_eku and not certificate.get("client_auth", False):
            raise PermissionError("mTLS certificate is not valid for client authentication")

        subject = str(certificate.get("subject", "")).strip()
        spiffe_id = str(certificate.get("spiffe_id", "")).strip()
        trusted_subjects = set(self.security_settings.trusted_client_certificate_subjects)
        trusted_spiffe_ids = set(self.security_settings.trusted_client_spiffe_ids)
        if subject not in trusted_subjects and spiffe_id not in trusted_spiffe_ids:
            raise PermissionError("Client certificate subject is not trusted")

        now = datetime.now(timezone.utc)
        not_before = self._parse_timestamp(certificate.get("not_before"), "not_before")
        not_after = self._parse_timestamp(certificate.get("not_after"), "not_after")
        if now < not_before:
            raise PermissionError("Client certificate is not yet valid")
        if now >= not_after:
            raise PermissionError("Client certificate is expired")

    def process(self, request: dict[str, object]) -> dict[str, object]:
        path = str(request.get("path", ""))
        if not path.startswith("/api/") or not self.security_settings.require_mtls:
            return request
        if not request.get("client_certificate_verified", False):
            raise PermissionError("mTLS client verification is required")
        certificate = request.get("client_certificate")
        if not isinstance(certificate, dict):
            raise PermissionError("Client certificate metadata is required")
        self._verify_certificate(certificate)
        request["client_certificate_subject"] = certificate.get("subject")
        request["client_spiffe_id"] = certificate.get("spiffe_id")
        return request
