from __future__ import annotations

import unittest

from services.offline_sync_service.device.tamper_protection import TamperProtection
from services.offline_sync_service.hardware.tamper_sensor import TamperSensor


class TamperLockTests(unittest.TestCase):
    def test_tamper_detection_locks_device(self) -> None:
        protection = TamperProtection(sensor=TamperSensor(tampered=True))
        lock = protection.enforce()
        self.assertTrue(lock.locked)
        self.assertEqual(lock.reason, "tamper_detected")


if __name__ == "__main__":
    unittest.main()
