"""VVPAT generation helpers."""

from __future__ import annotations

from dataclasses import dataclass

from services.print_service.qr_embed import build_signed_qr_payload


@dataclass(frozen=True)
class VVPATReceipt:
    election_id: str
    ballot_id: str
    human_readable_summary: str
    qr_payload: str


def build_vvpat_receipt(
    election_id: str,
    ballot_id: str,
    summary: str,
    signed_payload: dict[str, object],
    signature: str,
) -> VVPATReceipt:
    return VVPATReceipt(
        election_id=election_id,
        ballot_id=ballot_id,
        human_readable_summary=summary,
        qr_payload=build_signed_qr_payload(signed_payload, signature),
    )
