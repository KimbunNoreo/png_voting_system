"""Request sanitization middleware."""

from __future__ import annotations


class RequestSanitizerMiddleware:
    """Normalize request fields before zero-trust policy evaluation."""

    _CONTROL_CHARACTERS = ("\x00", "\r", "\n")

    def _sanitize_scalar(self, value: object, *, field_name: str) -> str:
        sanitized = str(value).strip()
        for control_character in self._CONTROL_CHARACTERS:
            if control_character in sanitized:
                raise ValueError(f"{field_name} contains prohibited control characters")
        return sanitized

    def process(self, request: dict[str, object]) -> dict[str, object]:
        request["path"] = self._sanitize_scalar(request.get("path", ""), field_name="path")
        request["body"] = self._sanitize_scalar(request.get("body", ""), field_name="body")
        request["method"] = self._sanitize_scalar(request.get("method", "GET"), field_name="method").upper()

        query = request.get("query", {})
        if isinstance(query, dict):
            request["query"] = {
                self._sanitize_scalar(key, field_name="query key"): self._sanitize_scalar(
                    value,
                    field_name=f"query value for {key}",
                )
                for key, value in query.items()
            }
        else:
            request["query"] = self._sanitize_scalar(query, field_name="query")

        headers = request.get("headers", {})
        if not isinstance(headers, dict):
            raise ValueError("headers must be a dictionary")
        sanitized_headers: dict[str, str] = {}
        for key, value in headers.items():
            sanitized_key = self._sanitize_scalar(key, field_name="header name")
            sanitized_value = self._sanitize_scalar(value, field_name=f"header {sanitized_key}")
            sanitized_headers[sanitized_key] = sanitized_value
        request["headers"] = sanitized_headers
        return request
