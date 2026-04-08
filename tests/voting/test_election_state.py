from __future__ import annotations

import unittest

from election_state.audit_phase_changes import record_phase_change
from election_state.state_machine import ElectionStateMachine


class ElectionStateTests(unittest.TestCase):
    def test_valid_phase_progression(self) -> None:
        machine = ElectionStateMachine(election_id="e1")
        machine.transition_to("verification")
        machine.transition_to("voting")
        self.assertEqual(machine.phase, "voting")

    def test_invalid_phase_transition_rejected(self) -> None:
        machine = ElectionStateMachine(election_id="e1")
        with self.assertRaises(ValueError):
            machine.transition_to("counting")

    def test_phase_change_audit_requires_multiple_approvers(self) -> None:
        with self.assertRaises(ValueError):
            record_phase_change("e1", "verification", "voting", ("official-1",))


if __name__ == "__main__":
    unittest.main()
