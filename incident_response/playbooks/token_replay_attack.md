# Token Replay Attack Playbook

## Trigger

- Replay detector reports the same `token_hash` from multiple devices
- Sync conflict resolution surfaces duplicate token use attempts
- Gateway or voting-service audit shows repeated submissions against one token

## Immediate Actions

1. Activate enhanced monitoring on the affected election and precinct scope.
2. Preserve related audit entries, replay alerts, and device identifiers.
3. If replay attempts are widespread or coordinated, evaluate global freeze activation.
4. Revoke compromised devices if device-specific fraud signals are present.

## Investigation Steps

1. Confirm the first accepted device and timestamp for the token hash.
2. Identify all later replay attempts and affected devices.
3. Review time-sync status and device attestation state for implicated devices.
4. Determine whether the issue originated from operator error, device compromise, or coordinated fraud.

## Recovery

- Keep the earliest valid token use only.
- Reject all later replay attempts deterministically.
- Re-attest or rotate credentials for suspect devices.
- Publish incident summary to observers when legally required.

## Evidence to Preserve

- replay detection records
- append-only audit hashes
- device revocation decisions
- custody log for exported evidence bundle
