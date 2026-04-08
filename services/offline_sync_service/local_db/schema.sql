-- Local offline vote cache schema.

CREATE TABLE IF NOT EXISTS offline_votes (
    vote_id TEXT PRIMARY KEY,
    election_id TEXT NOT NULL,
    ballot_id TEXT NOT NULL,
    token_hash TEXT NOT NULL,
    encrypted_vote BLOB NOT NULL,
    encrypted_key BLOB NOT NULL,
    iv BLOB NOT NULL,
    auth_tag BLOB NOT NULL,
    device_id TEXT NOT NULL,
    device_signature BLOB NOT NULL,
    kid TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_offline_votes_token_hash
    ON offline_votes (token_hash);
