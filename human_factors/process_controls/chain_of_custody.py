"""Human process chain-of-custody helpers."""

from __future__ import annotations

from legal_evidence.chain_of_custody_tracker import record_custody_event


def transfer_custody(actor: str, action: str):
    return record_custody_event(actor, action)
