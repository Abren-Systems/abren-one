from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.organizations.models import Membership


@dataclass(frozen=True)
class MembershipResult:
    """Read DTO for membership details (§3.4, §5.1)."""

    id: UUID
    organization_id: UUID
    user_id: UUID
    role: str
    status: str
    is_active: bool


def execute(*, organization_id: UUID, user_id: UUID) -> MembershipResult | None:
    """Retrieve a user's membership in a specific organization.

    Returns None if no membership exists.
    """
    try:
        membership = Membership.objects.select_related("organization").get(
            organization_id=organization_id,
            user_id=user_id,
        )
    except Membership.DoesNotExist:
        return None

    return MembershipResult(
        id=membership.id,
        organization_id=membership.organization_id,
        user_id=membership.user_id,
        role=membership.role,
        status=membership.status,
        is_active=membership.is_active,
    )
