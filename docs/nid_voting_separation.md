# NID and Voting Separation

SecureVote PNG is designed so the external National ID system and the voting system remain separate trust domains.

## Core Rule

The NID system verifies identity. The voting system verifies eligibility artifacts and records votes. The voting domain must never become a general identity repository.

## Allowed NID Outputs into Voting

- signed eligibility token
- token metadata required for validation
- eligibility decision

## Prohibited in Voting Storage

- citizen name
- address
- date of birth
- biometric templates
- national identity number

## Implementation Mapping

- `services/nid_client/` handles communication with the external NID service
- `services/voting_service/services/verification_gateway.py` strips sensitive claims
- `services/voting_service/models/vote.py` persists only encrypted vote material and token hash

## Why This Matters

- secret ballot protection depends on the absence of an identity-vote join path
- public trust depends on proving that eligibility and ballot choice are isolated domains
