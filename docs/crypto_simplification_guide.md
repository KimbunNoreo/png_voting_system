# Crypto Simplification Guide

Phase 1 intentionally limits the cryptographic surface area to proven, auditable primitives.

## Approved Phase 1 Cryptography

- AES-256-GCM for vote payload confidentiality and integrity
- RSA-4096 for key wrapping, signatures, and token-related verification workflows
- SHA-256 for commitments, token hashes, and audit digests

## Explicitly Disabled

- Homomorphic tallying
- Zero-knowledge proofs
- Experimental or custom cryptographic schemes
- AI-driven trust scoring

## Design Rationale

- Smaller cryptographic surface improves auditability.
- Standard, widely reviewed primitives reduce implementation risk.
- Public and third-party verification is easier when encryption and signature paths are deterministic and conventional.

## Implementation Mapping

- `services/voting_service/crypto/phase1_standard.py`
- `services/voting_service/crypto/crypto_provider.py`
- `config/crypto_provider.py`

## Operational Notes

- Key IDs (`kid`) must be tracked with every encrypted vote artifact.
- Key rotation is allowed, but new keys must remain within the same approved Phase 1 primitive family.
- Optional Phase 2 and Phase 3 modules must remain disabled in Phase 1 deployments.
