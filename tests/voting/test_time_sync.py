from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from time_sync.drift_detection import detect_drift


class TimeSyncTests(unittest.TestCase):
    def test_detect_drift_within_threshold(self) -> None:
        trusted = datetime.now(timezone.utc)
        device = trusted - timedelta(seconds=30)
        result = detect_drift(device, trusted, threshold_seconds=120)
        self.assertTrue(result.within_threshold)

    def test_detect_drift_outside_threshold(self) -> None:
        trusted = datetime.now(timezone.utc)
        device = trusted - timedelta(minutes=10)
        result = detect_drift(device, trusted, threshold_seconds=120)
        self.assertFalse(result.within_threshold)


if __name__ == "__main__":
    unittest.main()
