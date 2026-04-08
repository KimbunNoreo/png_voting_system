from __future__ import annotations

import unittest

from legal_evidence.chain_of_custody_tracker import record_custody_event


class ChainOfCustodyTests(unittest.TestCase):
    def test_custody_event_records_actor_and_action(self) -> None:
        event = record_custody_event("observer-1", "received_bundle")
        self.assertEqual(event.actor, "observer-1")
        self.assertEqual(event.action, "received_bundle")


if __name__ == "__main__":
    unittest.main()
