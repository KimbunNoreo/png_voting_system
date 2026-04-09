"""Token validation facade."""

from services.nid_client.client import NIDClient


def validate_token(token: str, client: NIDClient | None = None) -> dict[str, object]:
    return (client or NIDClient()).validate_token(token)
