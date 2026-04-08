"""Celery and broker configuration."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class CeleryConfig:
    broker_url: str = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
    result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    task_default_queue: str = "securevote-default"
    task_acks_late: bool = True
    worker_prefetch_multiplier: int = 1