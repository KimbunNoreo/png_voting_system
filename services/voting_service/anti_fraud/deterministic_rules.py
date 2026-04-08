"""Hard deterministic anti-fraud rules."""
from services.voting_service.services.deterministic_fraud import DeterministicFraudService, FraudDecision

def evaluate_rules(*, replay_detected: bool, device_revoked: bool, within_time_window: bool) -> FraudDecision:
    return DeterministicFraudService().evaluate(replay_detected=replay_detected, device_revoked=device_revoked, within_time_window=within_time_window)