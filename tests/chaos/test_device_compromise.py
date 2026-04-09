from __future__ import annotations

import unittest

from chaos_testing.device_failure_test import simulate_device_failure


class DeviceCompromiseChaosTests(unittest.TestCase):
    def test_device_failure_reported(self) -> None:
        result = simulate_device_failure("device-1", True)
        self.assertTrue(result["failed"])

    def test_device_failure_redacts_sensitive_diagnostics(self) -> None:
        result = simulate_device_failure(
            "device-1",
            True,
            diagnostics={"authorization": "Bearer secret", "sub": "citizen-5"},
        )
        self.assertEqual(result["diagnostics"]["authorization"], "[redacted]")
        self.assertEqual(result["diagnostics"]["sub"], "[redacted]")

    def test_device_failure_rejects_blank_device_id(self) -> None:
        with self.assertRaises(ValueError):
            simulate_device_failure(" ", True)


if __name__ == "__main__":
    unittest.main()
