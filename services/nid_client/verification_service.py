"""Verification service facade."""

from services.nid_client.client import NIDClient
from services.nid_client.models import VerificationRequest, VerificationResponse


def verify_user(request: VerificationRequest, client: NIDClient | None = None) -> VerificationResponse:
    return (client or NIDClient()).verify_user(request)