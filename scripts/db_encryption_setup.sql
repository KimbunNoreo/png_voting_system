-- Phase 1 PostgreSQL encryption bootstrap.
-- Uses pgcrypto-backed columns and leaves key management outside the database.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS encrypted_vote_store (
    vote_id UUID PRIMARY KEY,
    election_id TEXT NOT NULL,
    ballot_id TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    encrypted_vote BYTEA NOT NULL,
    encrypted_key BYTEA NOT NULL,
    iv BYTEA NOT NULL,
    auth_tag BYTEA NOT NULL,
    device_id TEXT NOT NULL,
    device_signature BYTEA NOT NULL,
    kid TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_encrypted_vote_store_election_id
    ON encrypted_vote_store (election_id);

CREATE INDEX IF NOT EXISTS idx_encrypted_vote_store_device_id
    ON encrypted_vote_store (device_id);
