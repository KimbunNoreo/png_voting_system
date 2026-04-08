"""Tracks which device signed which vote payload."""
from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class DeviceVoteSignature:
    vote_id: str
    device_id: str
    signature: str
    digest: str