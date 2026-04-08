# Token Replay Prevention

Token replay prevention is a mandatory control in SecureVote PNG because eligibility tokens are single-use voting artifacts.

## Strategy

- hash tokens before storage
- consume each token once
- detect repeated use across devices
- preserve first valid use and reject later attempts deterministically

## Online Path

- gateway enforces rate limits
- voting service hashes token and checks one-time-use registry
- replay detector records first-seen device

## Offline Path

- offline devices stage token-hash-linked encrypted votes
- sync conflict resolution merges on `token_hash`
- earliest accepted record wins
- later records are treated as replay attempts

## Implementation Mapping

- `services/voting_service/services/token_consumer.py`
- `services/voting_service/services/token_replay_detector.py`
- `services/offline_sync_service/sync/conflict_resolution.py`
- `tests/security/test_token_replay_global.py`
- `tests/offline/test_offline_token_replay.py`
