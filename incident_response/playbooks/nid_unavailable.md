# NID Unavailable Playbook

## Trigger

- repeated upstream verification failures
- NID circuit breaker opened
- upstream maintenance or confirmed outage

## Immediate Actions

1. confirm outage through health checks and gateway logs
2. preserve failure telemetry and audit artifacts
3. decide whether voting continues under approved fallback or pauses

## Fallback Rules

- fallback is not automatic
- KBA requires multi-person approval
- all fallback usage must be logged
- replay, audit, and rate-limit controls remain active

## Recovery

- restore normal NID validation as soon as upstream becomes stable
- review all fallback events after recovery
