"""Base settings and configuration assembly for SecureVote PNG."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import os

from config.ai_mode_config import AIModeConfig
from config.api_versioning import APIVersioningConfig
from config.audit_retention_policy import AuditRetentionPolicy
from config.cache import CacheConfig
from config.celery import CeleryConfig
from config.constants import APP_NAME
from config.crypto_key_id_config import CryptoKeyConfig
from config.database import DatabaseConfig
from config.emergency_freeze_config import EmergencyFreezeConfig
from config.key_rotation_schedule import KeyRotationSchedule
from config.logging import LoggingConfig
from config.nid_integration import NIDIntegrationConfig
from config.rate_limit_voting import VotingRateLimitConfig
from config.secrets_manager import SecretsManagerConfig
from config.security import SecurityConfig
from config.staged_rollout import StagedRolloutConfig
from services.audit_service import AuditSettings
from services.offline_sync_service.settings import SyncSettings
from services.voting_service.settings import VotingAppSettings


@dataclass(frozen=True)
class BaseSettings:
    """Strongly typed base settings used by service modules and Django."""

    app_name: str = APP_NAME
    debug: bool = False
    secret_key: str = field(default_factory=lambda: os.getenv("DJANGO_SECRET_KEY", "development-only-secret-key"))
    allowed_hosts: tuple[str, ...] = field(
        default_factory=lambda: tuple(filter(None, os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")))
    )
    installed_apps: tuple[str, ...] = (
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "rest_framework",
    )
    middleware: tuple[str, ...] = (
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    )
    security: SecurityConfig = field(default_factory=SecurityConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig.from_env)
    cache: CacheConfig = field(default_factory=CacheConfig)
    celery: CeleryConfig = field(default_factory=CeleryConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    rate_limit: VotingRateLimitConfig = field(default_factory=VotingRateLimitConfig)
    key_rotation: KeyRotationSchedule = field(default_factory=KeyRotationSchedule)
    emergency_freeze: EmergencyFreezeConfig = field(default_factory=EmergencyFreezeConfig)
    crypto_keys: CryptoKeyConfig = field(default_factory=CryptoKeyConfig)
    staged_rollout: StagedRolloutConfig = field(default_factory=StagedRolloutConfig)
    ai_mode: AIModeConfig = field(default_factory=AIModeConfig)
    nid_integration: NIDIntegrationConfig = field(default_factory=NIDIntegrationConfig)
    api_versioning: APIVersioningConfig = field(default_factory=APIVersioningConfig)
    secrets_manager: SecretsManagerConfig = field(default_factory=SecretsManagerConfig)
    audit_retention: AuditRetentionPolicy = field(default_factory=AuditRetentionPolicy)
    audit_service: AuditSettings = field(default_factory=AuditSettings)
    voting_service: VotingAppSettings = field(default_factory=VotingAppSettings)
    offline_sync_service: SyncSettings = field(default_factory=SyncSettings)

    def as_django_settings(self) -> dict[str, object]:
        security = self.security
        return {
            "DEBUG": self.debug,
            "SECRET_KEY": self.secret_key,
            "ALLOWED_HOSTS": list(self.allowed_hosts),
            "INSTALLED_APPS": list(self.installed_apps),
            "MIDDLEWARE": list(self.middleware),
            "DATABASES": self.database.as_django_dict(),
            "CACHES": self.cache.as_django_dict(),
            "LOGGING": self.logging.as_dict(),
            "SECURE_HSTS_SECONDS": 63072000,
            "SECURE_HSTS_INCLUDE_SUBDOMAINS": True,
            "SECURE_HSTS_PRELOAD": True,
            "SECURE_SSL_REDIRECT": security.ssl_redirect,
            "CSRF_COOKIE_SECURE": security.csrf_cookie_secure,
            "SESSION_COOKIE_SECURE": security.session_cookie_secure,
            "X_FRAME_OPTIONS": security.headers.x_frame_options,
            "SECURE_CONTENT_TYPE_NOSNIFF": True,
        }

    def export(self) -> dict[str, object]:
        return asdict(self)
