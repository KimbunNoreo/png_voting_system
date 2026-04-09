from __future__ import annotations

import unittest
from unittest.mock import patch

from services.nid_client.client import NIDClient
from services.nid_client.exceptions import NIDAuthenticationError, NIDClientError


class _FakeResponse:
    def __init__(self, *, status_code: int, text: str = "{}", json_payload: object | None = None) -> None:
        self.status_code = status_code
        self.text = text
        self._json_payload = json_payload if json_payload is not None else {}

    def json(self) -> object:
        if isinstance(self._json_payload, dict):
            return dict(self._json_payload)
        return self._json_payload


class _FakeHttpxClient:
    def __init__(self, responses: list[_FakeResponse]) -> None:
        self._responses = responses
        self.calls = 0

    def __enter__(self) -> "_FakeHttpxClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def request(self, method: str, path: str, json: dict[str, object] | None = None) -> _FakeResponse:
        index = min(self.calls, len(self._responses) - 1)
        self.calls += 1
        return self._responses[index]


class NIDClientRequestPolicyTests(unittest.TestCase):
    def test_request_retries_retryable_status_then_succeeds(self) -> None:
        fake_client = _FakeHttpxClient(
            [
                _FakeResponse(status_code=503, text="service unavailable"),
                _FakeResponse(status_code=200, json_payload={"eligible": True}),
            ]
        )
        with patch("services.nid_client.client.httpx.Client", return_value=fake_client), patch(
            "services.nid_client.client.time.sleep", return_value=None
        ):
            client = NIDClient()
            payload = client._request("GET", "/api/v1/eligibility/token-1")
        self.assertTrue(payload["eligible"])
        self.assertEqual(fake_client.calls, 2)

    def test_request_does_not_retry_non_retryable_client_error(self) -> None:
        fake_client = _FakeHttpxClient([_FakeResponse(status_code=400, text="bad request")])
        with patch("services.nid_client.client.httpx.Client", return_value=fake_client):
            client = NIDClient()
            with self.assertRaises(NIDClientError):
                client._request("GET", "/api/v1/eligibility/token-1")
        self.assertEqual(fake_client.calls, 1)

    def test_request_does_not_retry_authentication_error(self) -> None:
        fake_client = _FakeHttpxClient([_FakeResponse(status_code=401, text="unauthorized")])
        with patch("services.nid_client.client.httpx.Client", return_value=fake_client):
            client = NIDClient()
            with self.assertRaises(NIDAuthenticationError):
                client._request("GET", "/api/v1/eligibility/token-1")
        self.assertEqual(fake_client.calls, 1)

    def test_request_rejects_non_object_json_response(self) -> None:
        fake_client = _FakeHttpxClient([_FakeResponse(status_code=200, json_payload=["not", "an", "object"])])
        with patch("services.nid_client.client.httpx.Client", return_value=fake_client):
            client = NIDClient()
            with self.assertRaises(NIDClientError):
                client._request("GET", "/api/v1/eligibility/token-1")


if __name__ == "__main__":
    unittest.main()
