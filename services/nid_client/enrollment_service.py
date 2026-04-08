"""Enrollment service facade for controlled staging scenarios."""

from services.nid_client.client import NIDClient
from services.nid_client.models import EnrollmentRequest


def enroll_user(request: EnrollmentRequest, client: NIDClient | None = None) -> dict[str, object]:
    return (client or NIDClient()).enroll_user(request)