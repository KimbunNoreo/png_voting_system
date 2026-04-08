"""Global token replay helper."""
from services.voting_service.services.token_replay_detector import TokenReplayDetector

def detect(token_hash: str, device_id: str, detector: TokenReplayDetector):
    return detector.register(token_hash, device_id)