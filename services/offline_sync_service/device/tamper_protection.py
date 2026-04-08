"""Tamper detection and lock coordination."""

from __future__ import annotations

from services.offline_sync_service.device.device_lock import DeviceLock
from services.offline_sync_service.hardware.tamper_sensor import TamperSensor


class TamperProtection:
    def __init__(self, sensor: TamperSensor | None = None, lock: DeviceLock | None = None) -> None:
        self.sensor = sensor or TamperSensor()
        self.lock = lock or DeviceLock()

    def enforce(self) -> DeviceLock:
        if self.sensor.is_tampered():
            self.lock.activate("tamper_detected")
        return self.lock
