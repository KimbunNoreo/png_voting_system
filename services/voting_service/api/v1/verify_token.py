from services.voting_service.services.verification_gateway import VerificationGateway
def verify_token(token: str, gateway: VerificationGateway | None = None) -> dict[str, object]:
    return (gateway or VerificationGateway()).validate_voting_token(token)