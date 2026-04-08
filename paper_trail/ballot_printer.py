"""Paper ballot printing helpers."""

from __future__ import annotations

from services.print_service.vvpat import build_vvpat_receipt


def print_ballot_receipt(
    election_id: str,
    ballot_id: str,
    summary: str,
    signed_payload: dict[str, object],
    signature: str,
):
    return build_vvpat_receipt(election_id, ballot_id, summary, signed_payload, signature)
