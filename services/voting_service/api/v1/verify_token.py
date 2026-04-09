from services.voting_service.services.verification_gateway import VerificationGateway


def _require_non_empty_token(token: str) -> str:
    value = str(token).strip()
    if not value:
        raise ValueError("Voting token is required")
    return value


def verify_token(token: str, gateway: VerificationGateway | None = None) -> dict[str, object]:
    return (gateway or VerificationGateway()).validate_voting_token(_require_non_empty_token(token))
