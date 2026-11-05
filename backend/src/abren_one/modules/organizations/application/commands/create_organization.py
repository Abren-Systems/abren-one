from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.organizations.domain.exceptions import OrganizationError
from abren_one.modules.organizations.domain.value_objects import (
    MembershipRole,
    MembershipStatus,
    OrganizationStatus,
)
from abren_one.modules.organizations.models import Membership, Organization
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.common.context import ActorType, ExecutionContext


@dataclass(frozen=True)
class CreateOrganizationInput:
    """Input DTO for initial organization creation (§5.2, §5.3)."""

    context: ExecutionContext
    name: str
    slug: str


@dataclass(frozen=True)
class CreateOrganizationResult:
    organization_id: UUID
    slug: str


@transaction.atomic
def execute(data: CreateOrganizationInput) -> CreateOrganizationResult:
    """Provision a new organization.

    Invariants:
    - Initial organization provisioning has no prior org context (tenancy invariants 1 and 5 only, §5.3).
    - Organization slug must be unique.
    - If initiated by a user, creates the founding owner membership.
    - Records audit event.
    """
    if Organization.objects.filter(slug=data.slug).exists():
        raise OrganizationError(f"Organization with slug '{data.slug}' already exists.")

    org = Organization.objects.create(
        name=data.name,
        slug=data.slug,
        status=OrganizationStatus.ACTIVE.value,
    )

    # Founding user receives Owner membership
    if data.context.actor_type == ActorType.USER and data.context.actor_id:
        Membership.objects.create(
            organization=org,
            user_id=data.context.actor_id,
            role=MembershipRole.OWNER.value,
            status=MembershipStatus.ACTIVE.value,
        )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=org.id,
        action="organization.created",
        target_type="organizations.Organization",
        target_id=org.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"slug": org.slug, "name": org.name},
    )

    return CreateOrganizationResult(organization_id=org.id, slug=org.slug)
