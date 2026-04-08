from __future__ import annotations

import unittest


class NIDMockTests(unittest.TestCase):
    def test_mock_response_shape(self) -> None:
        response = {"verification_token": "abc", "token_id": "1", "eligible": True}
        self.assertIn("verification_token", response)
        self.assertTrue(response["eligible"])


if __name__ == "__main__":
    unittest.main()
