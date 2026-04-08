from __future__ import annotations

import unittest

from hardware.device_lock_circuit import DeviceLockCircuit
from hardware.tamper_detection import detect_tamper
from hardware.tpm_integration import TPMIntegration


class HardwareControlTests(unittest.TestCase):
    def test_tpm_seal_and_unseal(self) -> None:
        tpm = TPMIntegration()
        tpm.seal_key("k1", "secret")
        self.assertEqual(tpm.unseal_key("k1"), "secret")

    def test_tamper_detection_and_lock_circuit(self) -> None:
        self.assertTrue(detect_tamper(sensor_triggered=True, enclosure_open=False))
        circuit = DeviceLockCircuit()
        circuit.engage()
        self.assertTrue(circuit.engaged)


if __name__ == "__main__":
    unittest.main()
