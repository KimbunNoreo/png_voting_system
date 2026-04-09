from __future__ import annotations

import unittest

from services.audit_service import WORMLogger
from services.voting_service.api.v1.emergency_freeze import deactivate_freeze
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

    def test_freeze_activation_rejects_more_than_five_approvals(self) -> None:
        service = EmergencyFreezeService()
        state = ElectionState(election_id="e1", phase="voting", freeze_active=False)
        with self.assertRaises(ValueError):
            service.activate(state, "incident", 6)

    def test_freeze_deactivation_requires_approval_bounds(self) -> None:
        service = EmergencyFreezeService()
        active_state = ElectionState(election_id="e1", phase="voting", freeze_active=True)
        with self.assertRaises(ValueError):
            service.deactivate(active_state, "restore", 2)
        with self.assertRaises(ValueError):
            service.deactivate(active_state, "restore", 6)
        released_state, _ = service.deactivate(active_state, "restore", 3)
        self.assertFalse(released_state.freeze_active)

    def test_deactivate_freeze_api_wrapper_enforces_validation(self) -> None:
        service = EmergencyFreezeService()
        active_state = ElectionState(election_id="e1", phase="voting", freeze_active=True)
        with self.assertRaises(ValueError):
            deactivate_freeze(active_state, " ", 3, service=service)
        with self.assertRaises(ValueError):
            deactivate_freeze(active_state, "restore", 7, service=service)
        released_state, _ = deactivate_freeze(active_state, "restore", 3, service=service)
        self.assertFalse(released_state.freeze_active)


if __name__ == "__main__":
    unittest.main()
