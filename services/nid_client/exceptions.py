"""Domain exceptions for NID client operations."""

class NIDClientError(Exception):
    """Base error for NID client failures."""


class NIDAuthenticationError(NIDClientError):
    """Raised when the NID service rejects client authentication."""


class NIDValidationError(NIDClientError):
    """Raised when a token or response fails validation."""


class NIDUnavailableError(NIDClientError):
    """Raised when the NID service is unavailable or tripped open."""


class NIDEligibilityError(NIDClientError):
    """Raised when eligibility cannot be determined safely."""