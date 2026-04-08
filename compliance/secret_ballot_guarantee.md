# Secret Ballot Guarantee

SecureVote PNG Phase 1 preserves ballot secrecy by separating identity verification from vote storage and tallying.

## Enforced Conditions

- The external NID system performs identity verification.
- The voting domain stores only:
  - `token_hash`
  - encrypted vote payloads
  - device signatures
  - audit metadata required for integrity and legal review
- No vote record contains name, address, biometric template, or national identity number.

## Technical Controls

- `verification_gateway` strips sensitive claims before the voting flow uses token data.
- `Vote` model structure excludes identity-bearing fields by design.
- Public verification exposes commitments and hashes only.
- Audit data is integrity-focused and not identity-indexed by voter.

## Operational Controls

- Observer access is read-only.
- Emergency procedures may pause or freeze voting, but they do not authorize identity-vote linkage.
- Compliance tests assert that core vote structures remain free of direct identity fields.
