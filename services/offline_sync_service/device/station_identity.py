"""Station identity with TPM-backed keys."""

from __future__ import annotations

from dataclasses import dataclass

from services.voting_service.device.key_storage import DeviceKeyStorage


@dataclass
class StationIdentity:
    station_id: str
    key_storage: DeviceKeyStorage

    @classmethod
    def create(cls, station_id: str) -> "StationIdentity":
        return cls(station_id=station_id, key_storage=DeviceKeyStorage())
