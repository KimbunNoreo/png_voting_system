"""QR embedding helpers for printed receipts."""

from __future__ import annotations

import json


def build_signed_qr_payload(payload: dict[str, object], signature: str) -> str:
    return json.dumps({"payload": payload, "signature": signature}, sort_keys=True)
