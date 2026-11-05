from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.organizations.domain.exceptions import (
    CannotRevokeLastOwnerError,
    MembershipNotFoundError,
)
from abren_one.modules.organizations.domain.policies import can_revoke_membership
from abren_one.modules.organizations.domain.value_objects import (
    MembershipRole,
    MembershipStatus,
)
from abren_one.modules.organizations.models import Membership
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class RevokeMembershipInput:
    context: ExecutionContext
    membership_id: UUID


@dataclass(frozen=True)
class RevokeMembershipResult:
    membership_id: UUID


@transaction.atomic
def execute(data: RevokeMembershipInput) -> RevokeMembershipResult:
    """Revoke a user's membership (§5.2).

    Invariants:
    - Target membership must belong to the active organization.
    - Cannot revoke the last active owner of the organization.
    """
    assert data.context.organization_id is not None, "Organization context is required."

    try:
        membership = Membership.objects.get(
            id=data.membership_id,
            organization_id=data.context.organization_id,
        )
    except Membership.DoesNotExist as exc:
        raise MembershipNotFoundError(f"Membership {data.membership_id} not found.") from exc

    role = MembershipRole(membership.role)
    if role == MembershipRole.OWNER:
        active_owners = Membership.objects.filter(
            organization_id=data.context.organization_id,
            role=MembershipRole.OWNER.value,
            status=MembershipStatus.ACTIVE.value,
        ).count()
        if not can_revoke_membership(role, active_owners):
            raise CannotRevokeLastOwnerError("Cannot revoke the last active owner of an organization.")

    membership.status = MembershipStatus.REVOKED.value
    membership.save(update_fields=["status", "updated_at"])

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=data.context.organization_id,
        action="membership.revoked",
        target_type="organizations.Membership",
        target_id=membership.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"user_id": str(membership.user_id)},
    )

    return RevokeMembershipResult(membership_id=membership.id)
