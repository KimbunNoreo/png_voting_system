from __future__ import annotations

import unittest

from services.voting_service.services.device_revocation_service import DeviceRevocationService


class DeviceRevocationTests(unittest.TestCase):
    def test_revoked_device_is_rejected(self) -> None:
        service = DeviceRevocationService()
        service.revoke("device-1", "compromised")
        with self.assertRaises(ValueError):
            service.assert_not_revoked("device-1")


if __name__ == "__main__":
    unittest.main()
