-- Append-only ledger table for operational audit events.

CREATE TABLE IF NOT EXISTS audit_ledger (
    entry_id UUID PRIMARY KEY,
    event_type TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    previous_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION prevent_audit_ledger_mutation()
RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'audit_ledger is append-only';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS audit_ledger_no_update ON audit_ledger;
CREATE TRIGGER audit_ledger_no_update
BEFORE UPDATE OR DELETE ON audit_ledger
FOR EACH ROW EXECUTE FUNCTION prevent_audit_ledger_mutation();
