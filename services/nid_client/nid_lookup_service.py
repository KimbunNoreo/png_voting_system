"""Eligibility lookup facade."""

from services.nid_client.client import NIDClient


def check_eligibility(token: str, client: NIDClient | None = None) -> bool:
    return (client or NIDClient()).check_eligibility(token)