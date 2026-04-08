# Key Escrow Policy

Key escrow exists only to support regulated recovery and continuity scenarios.

## Policy Requirements

- recovery requires multiple distinct approvers
- escrowed material must be split into shares
- access to escrow records must be auditable
- recovered keys must remain within approved Phase 1 crypto policy

## Implementation Alignment

- `key_management/shamir_secret_sharing.py`
- `key_management/key_escrow.py`
- `key_management/recovery_authorization.py`
- `key_management/audit_key_access.py`

## Restrictions

- escrow may not be used to associate voters with ballots
- escrow access may not bypass freeze or audit requirements
