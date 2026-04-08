"""Election result commitment helpers."""

from __future__ import annotations

import hashlib
import json


def build_commitment(payload: dict[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
