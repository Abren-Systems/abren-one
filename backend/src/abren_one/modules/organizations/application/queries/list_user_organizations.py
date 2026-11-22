from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.organizations.models import Membership


@dataclass(frozen=True)
class UserOrganizationResult:
    organization_id: UUID
    name: str
    slug: str
    role: str
    status: str
    is_active: bool


def execute(
    *,
    user_id: UUID,
    limit: int = 100,
    offset: int = 0,
) -> list[UserOrganizationResult]:
    """List all organizations that a user has active membership in."""
    memberships = (
        Membership.objects.filter(user_id=user_id, status="active")
        .select_related("organization")
        .order_by("organization__name")[offset : offset + limit]
    )
    return [
        UserOrganizationResult(
            organization_id=m.organization.id,
            name=m.organization.name,
            slug=m.organization.slug,
            role=m.role,
            status=m.status,
            is_active=m.organization.is_active,
        )
        for m in memberships
    ]
