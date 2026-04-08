from __future__ import annotations

import unittest

from public_verifier_cli.verifier import run_verification
from public_verification.result_hash_publisher import publish_result_hash
from services.audit_service.logger.worm_logger import WORMLogger


class PublicVerifierCLITests(unittest.TestCase):
    def test_verifier_reports_clean_reconciliation(self) -> None:
        tally = {"candidate-a": 9, "candidate-b": 3}
        publication = publish_result_hash("e2", tally)
        logger = WORMLogger()
        logger.append("results_published", {"election_id": "e2"})
        result = run_verification("e2", tally, publication.result_hash, logger.entries(), tally)
        self.assertTrue(result["result_hash_valid"])
        self.assertTrue(result["audit_log_valid"])
        self.assertEqual(result["paper_vs_digital_delta"], {"candidate-a": 0, "candidate-b": 0})


if __name__ == "__main__":
    unittest.main()
