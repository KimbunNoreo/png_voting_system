# Public Verification

SecureVote PNG exposes integrity artifacts that allow public and third-party review without exposing ballot secrecy or identity data.

## Publicly Verifiable Artifacts

- election result hash commitments
- published audit digests
- signed audit exports
- paper-vs-digital reconciliation results

## Verification Paths

- `public_verification/` publishes result and audit commitments
- `public_verifier_cli/` verifies result hashes, signatures, audit chains, and paper-trail comparisons
- observer endpoints expose read-only audit views

## Non-Disclosure Requirements

- public verification must never reveal voter identity
- verification APIs must not expose raw NID responses
- published data must be commitment-oriented rather than identity-oriented

## Independent Validation Flow

1. retrieve published result hash
2. obtain tally or disclosed result dataset
3. recompute commitment locally
4. validate audit log chain
5. compare paper-trail counts against digital result counts
