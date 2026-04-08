"""Typed request and response models for the NID client."""

from services.nid_client.models.enrollment_request import EnrollmentRequest
from services.nid_client.models.nid_error import NIDError
from services.nid_client.models.verification_request import VerificationRequest
from services.nid_client.models.verification_response import VerificationResponse

__all__ = [
    "EnrollmentRequest",
    "NIDError",
    "VerificationRequest",
    "VerificationResponse",
]