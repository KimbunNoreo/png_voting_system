"""Base Django settings for the securevote scaffold."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "unsafe-development-key"
DEBUG = False
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "services.api_gateway.routing"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rest_framework",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "data" / "offline_db.sqlite",
    }
}
TIME_ZONE = "Pacific/Port_Moresby"
USE_TZ = True
