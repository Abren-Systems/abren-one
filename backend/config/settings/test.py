"""
Test settings for Abren One.

Uses in-memory SQLite and fast password hasher.
"""

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Debug — off for tests to match production behavior
# ---------------------------------------------------------------------------
DEBUG = False

SECRET_KEY = "django-insecure-test-key-do-not-use-in-production"  # noqa: S105

# ---------------------------------------------------------------------------
# Database — in-memory SQLite
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# ---------------------------------------------------------------------------
# Fast password hasher for tests
# ---------------------------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# ---------------------------------------------------------------------------
# Disable migrations in tests for speed (use --create-db when needed)
# ---------------------------------------------------------------------------
# Uncomment to skip migrations and create tables directly:
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# MIGRATION_MODULES = DisableMigrations()
