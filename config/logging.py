"""Structured logging configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoggingConfig:
    level: str = "INFO"
    audit_logger_name: str = "securevote.audit"
    application_logger_name: str = "securevote.app"

    def as_dict(self) -> dict[str, object]:
        formatter = {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"plain": formatter},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "plain",
                }
            },
            "loggers": {
                self.application_logger_name: {"handlers": ["console"], "level": self.level},
                self.audit_logger_name: {"handlers": ["console"], "level": self.level},
            },
        }