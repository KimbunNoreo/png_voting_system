"""Paper scanner integration wrappers."""

from __future__ import annotations

from services.print_service.paper_scanner import scan_receipt


def scan_paper_ballot(raw_text: str) -> dict[str, str]:
    return scan_receipt(raw_text)
