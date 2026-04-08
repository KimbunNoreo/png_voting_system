"""Publish daily audit hashes for public observer review."""

from __future__ import annotations

from dataclasses import dataclass

from public_verification.hash_commitment import build_commitment


@dataclass(frozen=True)
class PublishedAuditHash:
    device_id: str
    day: str
    digest: str


def publish_audit_hash(device_id: str, day: str, raw_digest: str) -> PublishedAuditHash:
    digest = build_commitment({"device_id": device_id, "day": day, "raw_digest": raw_digest})
    return PublishedAuditHash(device_id=device_id, day=day, digest=digest)
