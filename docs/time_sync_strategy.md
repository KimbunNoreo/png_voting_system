# Time Synchronization Strategy

Offline voting devices depend on trusted time to enforce election windows, prevent replay confusion, and support audit reconstruction.

## Sources

- network time when available
- trusted cached time for disconnected operation
- hardware-backed trusted time modules where deployed

## Controls

- device time is validated against a trusted source before sensitive operations
- drift outside configured thresholds is rejected
- cached trusted time expires after a bounded TTL
- time events are recorded for later audit review

## Implementation Mapping

- `time_sync/trusted_time_source.py`
- `time_sync/drift_detection.py`
- `time_sync/offline_time_cache.py`
- `time_sync/time_audit.py`
- `services/voting_service/services/time_sync_validator.py`

## Failure Handling

- excessive drift should block vote submission until corrected
- drift incidents must be auditable
- large-scale drift across devices may justify targeted lockout or emergency freeze evaluation
