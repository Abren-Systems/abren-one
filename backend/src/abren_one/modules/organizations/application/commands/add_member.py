from dataclasses import dataclass
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db import transaction

from abren_one.modules.organizations.domain.exceptions import (
    DuplicateMembershipError,
    OrganizationError,
)
from abren_one.modules.organizations.domain.value_objects import (
    MembershipRole,
    MembershipStatus,
)
from abren_one.modules.organizations.models import Membership, Organization
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.common.context import ExecutionContext

User = get_user_model()


@dataclass(frozen=True)
class AddMemberInput:
    context: ExecutionContext
    user_id: UUID
    role: str = MembershipRole.MEMBER.value


@dataclass(frozen=True)
class AddMemberResult:
    membership_id: UUID


@transaction.atomic
def execute(data: AddMemberInput) -> AddMemberResult:
    """Add a member to the organization (§5.1, §5.2)."""
    if data.context.organization_id is None:
        raise OrganizationError("Organization context is required.")

    org = Organization.objects.get(id=data.context.organization_id)
    try:
        user = User.objects.get(id=data.user_id)
    except User.DoesNotExist as exc:
        raise OrganizationError(f"User {data.user_id} does not exist.") from exc

    if Membership.objects.filter(organization=org, user=user).exists():
        raise DuplicateMembershipError(f"User {user.username} is already a member of this organization.")

    membership = Membership.objects.create(
        organization=org,
        user=user,
        role=data.role,
        status=MembershipStatus.ACTIVE.value,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=org.id,
        action="member.added",
        target_type="organizations.Membership",
        target_id=membership.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"user_id": str(user.id), "role": data.role},
    )

    return AddMemberResult(membership_id=membership.id)
