# Time Synchronization Compliance

Time control is a legal and operational requirement for election integrity in offline-first deployments.

## Requirements

- voting operations must occur within approved election windows
- drift beyond policy thresholds must be rejected or remediated
- time corrections and drift incidents must be auditable
- trusted time caches must be bounded in duration

## Implementation Alignment

- `time_sync/`
- `services/voting_service/services/time_sync_validator.py`
- `tests/voting/test_time_sync.py`

## Audit Expectations

- record trusted source used
- record measured drift
- record whether the action was accepted or rejected
