from __future__ import annotations

import unittest

from paper_trail.manual_recount import recount_ballots
from paper_trail.paper_vs_digital_reconcile import reconcile


class PaperReconciliationTests(unittest.TestCase):
    def test_recount_and_reconcile(self) -> None:
        paper_counts = recount_ballots(["candidate-a", "candidate-a", "candidate-b"])
        delta = reconcile(paper_counts, {"candidate-a": 2, "candidate-b": 1})
        self.assertEqual(delta["candidate-a"], 0)
        self.assertEqual(delta["candidate-b"], 0)


if __name__ == "__main__":
    unittest.main()
