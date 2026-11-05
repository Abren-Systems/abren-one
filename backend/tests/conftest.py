"""Shared Django test fixtures for unit, integration, and API tests.

Place factories (``factory_boy``), common fixtures (authenticated client,
organization context), and helpers here so module-level test suites can
use them without duplication.

See ``backend/tests/architecture/conftest.py`` for architecture-specific
fixtures (those tests run without Django).
"""

from __future__ import annotations
