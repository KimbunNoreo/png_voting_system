from __future__ import annotations

import unittest

from public_verifier_cli.verifier import run_verification
from public_verification.result_hash_publisher import publish_result_hash
from services.audit_service.logger.worm_logger import WORMLogger


class VerifierTests(unittest.TestCase):
    def test_verifier_reports_valid_result_and_audit_chain(self) -> None:
        tally = {"candidate-a": 5}
        publication = publish_result_hash("e1", tally)
        logger = WORMLogger()
        logger.append("vote_cast", {"vote_id": "v1"})
        result = run_verification("e1", tally, publication.result_hash, logger.entries(), {"candidate-a": 5})
        self.assertTrue(result["result_hash_valid"])
        self.assertTrue(result["audit_log_valid"])


if __name__ == "__main__":
    unittest.main()
