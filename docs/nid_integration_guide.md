# NID Integration Guide

This guide describes how the voting domain interacts with the external National ID service during Phase 1.

## Connection Model

- outbound calls only through `services/nid_client/`
- mTLS for service authentication
- API key support for upstream authorization
- retry with bounded backoff
- circuit breaker on repeated failures

## Main Operations

### Verify User

- request includes citizen reference, election context, device context, and biometric assertion reference
- upstream returns a signed verification token and eligibility result

### Validate Token

- voting service validates token structure and expiry
- eligibility is confirmed through the NID lookup path or cached result
- sensitive claims are removed before the voting flow continues

### Fallback

- if the NID service is unavailable, fallback requires explicit KBA plus multi-person approval
- fallback must be logged and must not bypass replay, rate-limit, or audit rules

## Implementation Mapping

- `services/nid_client/client.py`
- `services/nid_client/token_validator.py`
- `services/nid_client/circuit_breaker/`
- `services/voting_service/services/verification_gateway.py`
