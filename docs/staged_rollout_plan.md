# Staged Rollout Plan

Phase 1 is the only permitted deployment mode for the current codebase.

## Phase 1 Scope

- deterministic decision logic only
- AES-256-GCM and RSA-4096 only
- no AI-assisted voting or fraud adjudication
- no homomorphic tallying
- no zero-knowledge proofs

## Rollout Gates

1. cryptographic tests pass
2. replay and rate-limit protections pass
3. emergency freeze controls pass
4. public verification path is operational
5. audit log chain validation succeeds

## Rollback Philosophy

- rollback means freezing, pausing, or reverting operational state within Phase 1
- rollback does not activate Phase 2 or Phase 3 capabilities
- any emergency rollback must remain compatible with the current approved crypto profile
