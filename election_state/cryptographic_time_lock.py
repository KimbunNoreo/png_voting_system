"""Time-lock helpers for auditable phase commitments."""

from __future__ import annotations

import hashlib


def build_time_lock_commitment(election_id: str, phase: str, timestamp_iso: str) -> str:
    value = f"{election_id}:{phase}:{timestamp_iso}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
