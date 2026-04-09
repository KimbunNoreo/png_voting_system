from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from services.voting_service.services.time_sync_validator import TimeSyncValidator


class TimeSyncValidatorTests(unittest.TestCase):
    def test_rejects_non_positive_drift_threshold(self) -> None:
        with self.assertRaises(ValueError):
            TimeSyncValidator(max_drift_seconds=0)

    def test_accepts_timezone_aware_timestamps_within_threshold(self) -> None:
        trusted = datetime.now(timezone.utc)
        device = trusted - timedelta(seconds=30)
        TimeSyncValidator(max_drift_seconds=120).validate(device, trusted)

    def test_rejects_drift_outside_threshold(self) -> None:
        trusted = datetime.now(timezone.utc)
        device = trusted - timedelta(seconds=121)
        with self.assertRaises(ValueError):
            TimeSyncValidator(max_drift_seconds=120).validate(device, trusted)

    def test_rejects_naive_device_time(self) -> None:
        trusted = datetime.now(timezone.utc)
        naive_device = datetime.now()
        with self.assertRaises(ValueError):
            TimeSyncValidator().validate(naive_device, trusted)

    def test_rejects_naive_trusted_time(self) -> None:
        aware_device = datetime.now(timezone.utc)
        naive_trusted = datetime.now()
        with self.assertRaises(ValueError):
            TimeSyncValidator().validate(aware_device, naive_trusted)


if __name__ == "__main__":
    unittest.main()
