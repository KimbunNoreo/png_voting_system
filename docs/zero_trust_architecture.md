# Zero Trust Architecture

SecureVote PNG is designed so that no component receives implicit trust from network location, deployment tier, or historical behavior.

## Principles

- Every service-to-service hop requires authenticated transport.
- Voting decisions are deterministic and independently auditable.
- Identity proofing remains outside the voting domain.
- Offline devices are treated as intermittently connected, not inherently trusted.

## Service Boundaries

- `api_gateway` terminates and validates incoming requests, enforces TLS and mTLS policy, applies rate limiting, and routes only to approved internal services or the external NID system.
- `nid_client` is the only code allowed to call the external NID service. It strips identity-bearing behavior from the voting service boundary by returning eligibility and token claims only.
- `voting_service` accepts only validated tokens and persists only token hashes, encrypted vote envelopes, device signatures, and audit metadata.
- `offline_sync_service` stages encrypted records locally and resolves conflicts by deterministic token-hash rules.
- `audit_service` maintains hash-chained append-only records for operational and legal review.

## Trust Controls

- TLS is mandatory for user and service traffic.
- mTLS is mandatory for internal API access paths.
- Authorization is checked at the edge and again at the service boundary.
- Device revocation, time drift validation, rate limits, and replay detection are treated as first-class deny conditions.
- Global emergency freeze is enforced both by stateful services and by gateway middleware.

## Offline Trust Model

- Offline stations maintain local encrypted stores and TPM-backed identity material.
- Reconnection does not imply acceptance; sync results are merged only after replay and conflict checks.
- Cached trusted time is bounded by TTL and validated against configured drift thresholds.

## Observability

- Critical operations generate audit entries with hash chaining.
- Public verification surfaces expose commitments and hashes, not privileged raw identity data.
- Observer access is read-only and separately credentialed.
