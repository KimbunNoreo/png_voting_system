"""Configuration package initializer with Phase 1 enforcement."""

from __future__ import annotations

import os

from config.base import BaseSettings
from config.development import settings as development_settings
from config.production import settings as production_settings
from config.testing import settings as testing_settings


def get_settings() -> BaseSettings:
    environment = os.getenv("SECUREVOTE_ENV", "development").lower()
    if environment == "production":
        return production_settings
    if environment == "testing":
        return testing_settings
    return development_settings


__all__ = ["BaseSettings", "get_settings"]