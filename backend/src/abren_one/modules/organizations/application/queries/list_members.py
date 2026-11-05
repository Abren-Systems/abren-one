from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.organizations.models import Membership


@dataclass(frozen=True)
class MemberSummaryResult:
    membership_id: UUID
    user_id: UUID
    username: str
    email: str
    role: str
    status: str
    is_active: bool


def execute(*, organization_id: UUID) -> list[MemberSummaryResult]:
    """List all members belonging to the organization."""
    memberships = (
        Membership.objects.filter(organization_id=organization_id).select_related("user").order_by("-created_at")
    )
    return [
        MemberSummaryResult(
            membership_id=m.id,
            user_id=m.user.id,
            username=m.user.username,
            email=m.user.email,
            role=m.role,
            status=m.status,
            is_active=m.is_active,
        )
        for m in memberships
    ]
