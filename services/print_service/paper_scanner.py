"""Paper scanner integration interface."""

from __future__ import annotations


def scan_receipt(raw_text: str) -> dict[str, str]:
    return {"scanned_text": raw_text.strip()}
