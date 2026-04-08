"""Daily audit generation for offline devices."""

from __future__ import annotations

from services.voting_service.models.vote import Vote
from services.voting_service.services.daily_audit import DailyAuditService


def generate_daily_audit(device_id: str, day: str, votes: list[Vote]):
    return DailyAuditService().build(device_id, day, votes)
