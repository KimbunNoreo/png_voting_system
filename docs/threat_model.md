# Threat Model

This document captures the main adversarial scenarios addressed by the Phase 1 SecureVote PNG implementation.

## Assets

- Vote confidentiality
- Ballot integrity
- Token uniqueness
- Device trust state
- Audit-chain integrity
- Public result commitments

## Adversaries

- Remote network attacker attempting to inject, replay, or tamper with requests
- Malicious insider attempting unauthorized phase changes or emergency actions
- Compromised offline device attempting duplicate submission or forged sync
- Service outage or dependency failure causing unsafe fallbacks

## Key Threats and Mitigations

### Token Replay

- Threat: the same NID-issued token is used on multiple devices or retried during sync.
- Mitigations:
  - token hashing and one-time consumption
  - global replay detector keyed on `token_hash`
  - offline conflict resolution favoring earliest accepted token use
  - replay audit events

### Identity Leakage into Voting Domain

- Threat: PII from NID responses is stored alongside vote data.
- Mitigations:
  - `verification_gateway` strips sensitive claims before use
  - vote model excludes identity fields by design
  - compliance tests assert absence of identity attributes in vote storage structures

### Device Compromise

- Threat: tampered device attempts to continue operating or uploading fraudulent records.
- Mitigations:
  - tamper detection with lock-only response
  - device revocation service
  - device signing and audit digests
  - re-attestation and secure-boot checks

### Network-Layer Abuse

- Threat: unauthenticated, malformed, or malicious traffic reaches internal services.
- Mitigations:
  - gateway TLS and mTLS checks
  - request sanitization and deterministic threat filters
  - per-token and per-device rate limits
  - network policy and service-mesh enforcement

### Dependency Outage

- Threat: external NID outage creates pressure to bypass controls.
- Mitigations:
  - retry policy with bounded backoff
  - circuit breaker
  - explicit fallback requiring KBA and multi-person approval
  - chaos tests for degraded modes

## Residual Risks

- Local reference implementations still require production hardening for hardware, PKI, and infrastructure deployment.
- Many documentation and operational files remain descriptive rather than regulator-ready.
