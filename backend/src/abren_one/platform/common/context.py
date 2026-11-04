"""
Execution context for Abren One business operations.

Provides the trusted identity and tenant context that every
business operation receives from the API boundary.
"""

from dataclasses import dataclass
from enum import StrEnum
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
