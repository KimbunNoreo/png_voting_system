"""Signed offline sync manifest generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json

from services.audit_service.payload_sanitizer import sanitize_audit_payload
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider


@dataclass(frozen=True)
class SyncManifest:
    """Signed summary of a sync batch emitted by an offline device."""

    device_id: str
    generated_at: str
    record_count: int
    token_hashes: tuple[str, ...]
    digest: str
    signature: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_sync_manifest(device_id: str, records: list[dict[str, object]], private_key_pem: str) -> SyncManifest:
    """Build a deterministic signed manifest for a sanitized sync batch."""

    sanitized_records = [sanitize_audit_payload(record) for record in records]
    token_hashes = tuple(sorted(str(record["token_hash"]) for record in sanitized_records))
    payload = {
        "device_id": device_id,
        "record_count": len(sanitized_records),
        "token_hashes": list(token_hashes),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    crypto = Phase1CryptoProvider()
    return SyncManifest(
        device_id=device_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        record_count=len(sanitized_records),
        token_hashes=token_hashes,
        digest=crypto.digest(canonical),
        signature=crypto.sign_bytes(canonical.encode("utf-8"), private_key_pem),
    )


def verify_sync_manifest(manifest: SyncManifest, public_key_pem: str) -> bool:
    """Verify the manifest signature against the canonical sync summary."""

    payload = {
        "device_id": manifest.device_id,
        "record_count": manifest.record_count,
        "token_hashes": list(manifest.token_hashes),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return Phase1CryptoProvider().verify_bytes(canonical.encode("utf-8"), manifest.signature, public_key_pem)
