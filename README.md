# securevote_png

Phase 1 scaffold for a PNG voting platform that integrates with an external NID system instead of reimplementing identity services. The repository is organized around a strict boundary: the NID system verifies identity, while the voting system validates eligibility tokens and stores no direct voter identity.

## Architecture

- `config/` centralizes Django, security, rollout, and NID integration settings.
- `services/nid_client/` is the only internal boundary intended to call the external NID APIs.
- `services/voting_service/` holds token validation, vote casting, tally, replay prevention, and result publication.
- `services/offline_sync_service/` models encrypted offline storage and later synchronization.
- `public_verifier_cli/` contains independent verification tooling for public artifacts.

## Phase 1 rules

- AES-256-GCM and RSA-4096 only
- AI scaffolding present but disabled
- Deterministic fraud rules only
- Multi-person authorization for critical actions
- Emergency freeze support
