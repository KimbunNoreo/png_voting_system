"""Cryptographic proof-of-time helpers."""

from __future__ import annotations

import hashlib


def build_time_proof(device_id: str, timestamp_iso: str, trusted_source: str) -> str:
    material = f"{device_id}:{timestamp_iso}:{trusted_source}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()
