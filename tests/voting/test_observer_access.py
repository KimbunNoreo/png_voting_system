from __future__ import annotations

import unittest

from services.voting_service.api.v1.observer_tally import observer_tally


class ObserverAccessTests(unittest.TestCase):
    def test_observer_can_read_tally(self) -> None:
        tally = observer_tally("observer", {"candidate-a": 4})
        self.assertEqual(tally["candidate-a"], 4)

    def test_non_observer_is_rejected(self) -> None:
        with self.assertRaises(PermissionError):
            observer_tally("admin", {"candidate-a": 4})


if __name__ == "__main__":
    unittest.main()
