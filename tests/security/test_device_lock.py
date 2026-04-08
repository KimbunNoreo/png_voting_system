from __future__ import annotations

import unittest

from services.offline_sync_service.device.device_lock import DeviceLock


class DeviceLockTests(unittest.TestCase):
    def test_device_lock_activates_without_destroying_state(self) -> None:
        lock = DeviceLock()
        lock.activate("tamper_detected")
        self.assertTrue(lock.locked)
        self.assertEqual(lock.reason, "tamper_detected")


if __name__ == "__main__":
    unittest.main()
