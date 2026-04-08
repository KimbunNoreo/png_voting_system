"""Duplicate token protection helpers."""
from services.voting_service.services.token_consumer import TokenConsumer

def is_duplicate(token_hash: str, token_consumer: TokenConsumer) -> bool:
    return token_consumer.is_consumed(token_hash)