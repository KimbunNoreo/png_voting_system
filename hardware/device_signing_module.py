"""Hardware-backed device signing wrapper."""

from __future__ import annotations

from services.voting_service.device.key_storage import DeviceKeyStorage
from services.voting_service.services.device_signing import DeviceSigningService


class DeviceSigningModule:
    def __init__(self) -> None:
        self.key_storage = DeviceKeyStorage()
        self.service = DeviceSigningService()

    def sign(self, vote_id: str, device_id: str, payload: dict[str, object]):
        return self.service.sign_vote(vote_id, device_id, payload, self.key_storage.private_key_pem())
