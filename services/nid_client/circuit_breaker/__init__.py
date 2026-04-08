"""Circuit breaker exports."""

from services.nid_client.circuit_breaker.breaker import CircuitBreaker
from services.nid_client.circuit_breaker.fallback import KBAMultiPersonFallback

__all__ = ["CircuitBreaker", "KBAMultiPersonFallback"]