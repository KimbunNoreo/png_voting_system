from __future__ import annotations

import unittest

from scripts.verify_build import build_digest, verify_build


class BuildVerificationTests(unittest.TestCase):
    def test_build_digest_verification(self) -> None:
        content = "artifact-content"
        digest = build_digest(content)
        self.assertTrue(verify_build(content, digest))


if __name__ == "__main__":
    unittest.main()
