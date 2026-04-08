# Time Drift Detected Playbook

## Trigger

- device time exceeds configured drift threshold
- cached trusted time has expired
- multiple devices show correlated drift anomalies

## Immediate Actions

1. block affected device from vote submission
2. record drift value and trusted source used
3. verify whether issue is isolated or systemic

## Investigation

- inspect trusted time source availability
- inspect device clock and hardware time module state
- review whether any recent votes require manual scrutiny

## Recovery

- resynchronize device time
- re-run validation before restoring service
- consider freeze or wider incident response if drift is widespread
