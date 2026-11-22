"""
Local development settings for Abren One.

Uses SQLite by default and enables debug toolbar.
Can be switched to PostgreSQL by setting USE_POSTGRES=1.
"""

import os

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG = True

SECRET_KEY = "django-insecure-local-development-key-do-not-use-in-production"  # noqa: S105

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # noqa: S104

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# ---------------------------------------------------------------------------
# Database — PostgreSQL when USE_POSTGRES is set, otherwise SQLite
# ---------------------------------------------------------------------------
if os.environ.get("USE_POSTGRES", "").lower() in {"1", "true", "yes"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DATABASE_NAME", "abren_one"),
            "USER": os.environ.get("DATABASE_USER", "abren"),
            "PASSWORD": os.environ.get("DATABASE_PASSWORD", "abren_secret_dev_pwd"),
            "HOST": os.environ.get("DATABASE_HOST", "localhost"),
            "PORT": os.environ.get("DATABASE_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

# ---------------------------------------------------------------------------
# Django Debug Toolbar (optional dev dependency)
# ---------------------------------------------------------------------------
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405
except ImportError:
    pass

INTERNAL_IPS = ["127.0.0.1"]

# ---------------------------------------------------------------------------
# DRF — add browsable API for development
# ---------------------------------------------------------------------------
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]
