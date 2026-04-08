from __future__ import annotations

import unittest

from services.voting_service.models.election_state import ElectionState
from services.voting_service.services.emergency_freeze_service import EmergencyFreezeService


class Phase1RollbackTests(unittest.TestCase):
    def test_phase1_rollback_uses_emergency_freeze_not_phase_upgrade(self) -> None:
        service = EmergencyFreezeService()
        state = ElectionState(election_id="e1", phase="voting", freeze_active=False)
        frozen_state, event = service.activate(state, "rollback", 3)
        self.assertTrue(frozen_state.freeze_active)
        self.assertEqual(event.reason, "rollback")


if __name__ == "__main__":
    unittest.main()
