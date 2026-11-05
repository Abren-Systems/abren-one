from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.organizations.domain.exceptions import (
    MembershipNotFoundError,
    OrganizationError,
)
from abren_one.modules.organizations.domain.policies import can_transition_membership_status
from abren_one.modules.organizations.domain.value_objects import MembershipStatus
from abren_one.modules.organizations.models import Membership
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class SuspendMembershipInput:
    context: ExecutionContext
    membership_id: UUID


@dataclass(frozen=True)
class SuspendMembershipResult:
    membership_id: UUID
    status: str


@transaction.atomic
def execute(data: SuspendMembershipInput) -> SuspendMembershipResult:
    """Suspend an active membership (§5.2)."""
    assert data.context.organization_id is not None, "Organization context is required."

    try:
        membership = Membership.objects.get(
            id=data.membership_id,
            organization_id=data.context.organization_id,
        )
    except Membership.DoesNotExist as exc:
        raise MembershipNotFoundError(f"Membership {data.membership_id} not found.") from exc

    current_status = MembershipStatus(membership.status)
    target_status = MembershipStatus.SUSPENDED
    if not can_transition_membership_status(current_status, target_status):
        raise OrganizationError(f"Cannot transition membership from {current_status.value} to {target_status.value}.")

    membership.status = target_status.value
    membership.save(update_fields=["status", "updated_at"])

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=data.context.organization_id,
        action="membership.suspended",
        target_type="organizations.Membership",
        target_id=membership.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"user_id": str(membership.user_id)},
    )

    return SuspendMembershipResult(membership_id=membership.id, status=membership.status)
