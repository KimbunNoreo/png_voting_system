# Emergency Freeze Policy

Emergency freeze is the system-wide control used to halt voting actions during severe integrity, safety, or legal incidents.

## Activation Rules

- minimum of three distinct approvals
- explicit reason must be recorded
- activation must be auditable
- gateway and service-layer enforcement must both apply

## Allowed Triggers

- widespread replay attack
- severe device compromise
- unresolved legal or operational emergency
- systemic time-sync failure affecting election integrity

## Implementation Alignment

- `services/voting_service/services/emergency_freeze_service.py`
- `services/api_gateway/middleware/emergency_freeze.py`
- `tests/security/test_emergency_freeze.py`

## Deactivation Rules

- same approval threshold as activation
- reason for release must be recorded
- post-incident review is required
