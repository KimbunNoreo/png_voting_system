from __future__ import annotations

import unittest

from services.audit_service import WORMLogger
from services.voting_service.models.election_state import ElectionState
from services.voting_service.services.emergency_freeze_service import EmergencyFreezeService


class EmergencyFreezeTests(unittest.TestCase):
    def test_freeze_activation_requires_approvals(self) -> None:
        service = EmergencyFreezeService()
        state = ElectionState(election_id="e1", phase="voting", freeze_active=False)
        with self.assertRaises(ValueError):
            service.activate(state, "incident", 2)
        new_state, _ = service.activate(state, "incident", 3)
        self.assertTrue(new_state.freeze_active)

    def test_freeze_activation_is_audited(self) -> None:
        logger = WORMLogger()
        service = EmergencyFreezeService(audit_logger=logger)
        state = ElectionState(election_id="e1", phase="voting", freeze_active=False)
        new_state, event = service.activate(state, "incident", 3)
        self.assertTrue(new_state.freeze_active)
        entry = logger.entries()[-1]
        self.assertEqual(entry.event_type, "emergency_freeze_activated")
        self.assertEqual(entry.payload["election_id"], event.election_id)


if __name__ == "__main__":
    unittest.main()
