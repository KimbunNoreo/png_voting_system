"""Offline vote signing wrapper."""

from __future__ import annotations

from services.voting_service.services.device_signing import DeviceSigningService


def sign_payload(vote_id: str, device_id: str, payload: dict[str, object], private_key_pem: str):
    return DeviceSigningService().sign_vote(vote_id, device_id, payload, private_key_pem)
