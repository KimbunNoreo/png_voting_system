"""Operational wrapper for device lock activation."""

from __future__ import annotations

from services.offline_sync_service.device.device_lock import DeviceLock


def lock(reason: str) -> DeviceLock:
    device_lock = DeviceLock()
    device_lock.activate(reason)
    return device_lock
