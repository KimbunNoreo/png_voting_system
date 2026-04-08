"""Development settings."""

from __future__ import annotations

from dataclasses import replace

from config.base import BaseSettings

settings = replace(BaseSettings(), debug=True)