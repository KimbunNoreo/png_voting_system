# Device Tamper Detected Playbook

## Trigger

- tamper sensor fired
- enclosure breach detected
- secure boot or attestation anomaly consistent with physical compromise

## Immediate Actions

1. lock device
2. preserve local encrypted store and audit state
3. isolate device from further voting activity

## Investigation

- review tamper telemetry
- inspect custody chain
- determine whether device revocation is required

## Recovery

- only restore after formal inspection and re-attestation
- rotate credentials if compromise is plausible
- reconcile paper and digital records for affected period if necessary
