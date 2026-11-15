"""
Execution context for Abren One business operations.

Provides the trusted identity and tenant context that every
business operation receives from the API boundary.
"""

import uuid
from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID


class ActorType(StrEnum):
    """Types of actors that can initiate operations."""

    USER = "user"
    SYSTEM = "system"
    INTEGRATION = "integration"
    ADMINISTRATOR = "administrator"


@dataclass(frozen=True)
class ExecutionContext:
    """Trusted execution identity for business operations.

    Constructed by the API boundary after authentication and
    tenant verification. Commands must not trust caller-supplied
    actor/org values without this.

    Rules:
    - Tenant-scoped business commands must require non-null organization_id.
    - A system or integration actor must have an explicit authorization policy.
    - Being a system actor does NOT imply unrestricted access.
    """

    actor_type: ActorType
    actor_id: UUID | None
    organization_id: UUID | None
    correlation_id: UUID


def build_execution_context(request: Any) -> ExecutionContext:
    """Build a trusted ExecutionContext from an authenticated HTTP request (§5.3).

    Inspects the request's authenticated user, tenant context (if established),
    and correlation ID.
    """
    user = getattr(request, "user", None)
    actor_id: UUID | None = None
    if user and getattr(user, "is_authenticated", False):
        actor_id = getattr(user, "id", None)

    org_id: UUID | None = None
    if hasattr(request, "org_context") and request.org_context is not None:
        org_id = getattr(request.org_context, "organization_id", None)

    correlation_id: UUID = getattr(request, "correlation_id", None) or uuid.uuid4()

    return ExecutionContext(
        actor_type=ActorType.USER,
        actor_id=actor_id,
        organization_id=org_id,
        correlation_id=correlation_id,
    )


__all__ = [
    "ActorType",
    "ExecutionContext",
    "build_execution_context",
]
