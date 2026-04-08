# Offline Device Security

Offline voting stations are designed for constrained connectivity, but not for relaxed trust requirements.

## Controls

- TPM-backed station identity
- secure local encrypted store
- device signing for vote payloads
- daily audit digest generation
- time drift validation
- tamper detection followed by lock, not destruction

## Tamper Response

- physical tamper triggers device lock
- locked devices require investigation before reuse
- suspicious devices may be revoked centrally

## Sync Security

- queued records remain encrypted locally
- sync uses deterministic conflict resolution
- replay checks are repeated during merge

## Implementation Mapping

- `services/offline_sync_service/device/`
- `services/offline_sync_service/hardware/`
- `services/voting_service/services/device_revocation_service.py`
- `time_sync/`
