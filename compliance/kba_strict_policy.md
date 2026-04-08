# KBA Strict Policy

Knowledge-based authentication is not a primary identity method in SecureVote PNG.

## Policy

- KBA is permitted only as a documented fallback when the external NID service is unavailable.
- KBA fallback requires multi-person approval.
- KBA use must be logged and reviewable.
- KBA results must not be used to weaken secret-ballot protections.

## Implementation Alignment

- `services/nid_client/circuit_breaker/fallback.py`
- `tests/nid_integration/test_fallback_kba.py`

## Prohibited Use

- KBA cannot replace the normal NID verification path during standard operations.
- KBA cannot justify bypassing token replay prevention or rate limits.
