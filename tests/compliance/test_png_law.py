from __future__ import annotations

import unittest

from services.voting_service.services.emergency_freeze_service import EmergencyFreezeService
from services.voting_service.models.election_state import ElectionState


class PNGLawComplianceTests(unittest.TestCase):
    def test_global_freeze_requires_multi_person_approval(self) -> None:
        service = EmergencyFreezeService()
        state = ElectionState(election_id="e1", phase="voting", freeze_active=False)
        with self.assertRaises(ValueError):
            service.activate(state, "legal incident", 2)
        activated_state, _ = service.activate(state, "legal incident", 3)
        self.assertTrue(activated_state.freeze_active)


if __name__ == "__main__":
    unittest.main()
