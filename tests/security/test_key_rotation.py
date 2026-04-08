from __future__ import annotations

import unittest

from config.key_rotation_schedule import KeyRotationSchedule


class KeyRotationTests(unittest.TestCase):
    def test_rotation_schedule_is_defined(self) -> None:
        schedule = KeyRotationSchedule()
        self.assertGreater(schedule.signing_rotation_days, 0)
        self.assertTrue(schedule.emergency_rotation_enabled)


if __name__ == "__main__":
    unittest.main()
