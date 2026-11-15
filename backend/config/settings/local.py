"""
Local development settings for Abren One.

Uses SQLite and enables debug toolbar.
"""

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG = True

SECRET_KEY = "django-insecure-local-development-key-do-not-use-in-production"  # noqa: S105

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # noqa: S104

# ---------------------------------------------------------------------------
# Database — SQLite for local development
# ---------------------------------------------------------------------------
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
