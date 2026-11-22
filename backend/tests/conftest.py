"""Shared Django test fixtures for unit, integration, and API tests.

Place factories (``factory_boy``), common fixtures (authenticated client,
organization context), and helpers here so module-level test suites can
use them without duplication.

See ``backend/tests/architecture/conftest.py`` for architecture-specific
fixtures (those tests run without Django).
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

import pytest

from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.fixture
def api_client() -> Any:
    """Return an unauthenticated DRF API client."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def test_user(db: Any) -> Any:
    """Create and return a standard test user."""
    from django.contrib.auth import get_user_model

    user_cls = get_user_model()
    return user_cls.objects.create_user(
        username=f"user_{uuid.uuid4().hex[:8]}",
        password="testpassword123",
    )


@pytest.fixture
def authenticated_client(api_client: Any, test_user: Any) -> Any:
    """Return an API client authenticated with `test_user`."""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def execution_context_factory() -> Callable[..., ExecutionContext]:
    """Factory fixture for quickly building test ExecutionContext instances."""

    def _make_context(
        *,
        actor_type: ActorType = ActorType.USER,
        actor_id: uuid.UUID | None = None,
        organization_id: uuid.UUID | None = None,
        correlation_id: uuid.UUID | None = None,
        actor_role: str | None = "admin",
    ) -> ExecutionContext:
        return ExecutionContext(
            actor_type=actor_type,
            actor_id=actor_id or uuid.uuid4(),
            organization_id=organization_id,
            correlation_id=correlation_id or uuid.uuid4(),
            actor_role=actor_role,
        )

    return _make_context
