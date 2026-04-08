"""Routes Phase 1 crypto requests by key identifier."""
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider
def get_provider_for_kid(kid: str) -> Phase1CryptoProvider:
    if not kid.startswith("phase1"):
        raise ValueError("Only Phase 1 crypto is enabled")
    return Phase1CryptoProvider()