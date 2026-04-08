# Election Phase Violation Playbook

## Trigger

- vote attempts outside the voting phase
- ballot access attempted during freeze or lock
- unauthorized phase transition request

## Immediate Actions

1. deny the operation
2. preserve phase-change audit records
3. verify whether the request was operator error or malicious activity

## Investigation

- inspect state machine transition history
- review approver records for recent phase changes
- confirm system clocks and freeze state

## Recovery

- correct phase only through authorized transition path
- notify observers if violation affected election confidence
- include incident in post-election review
