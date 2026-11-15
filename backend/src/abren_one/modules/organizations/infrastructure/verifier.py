from __future__ import annotations

from uuid import UUID

from abren_one.modules.organizations.application.queries.get_membership import (
    execute as get_membership_query,
)
from abren_one.platform.tenancy.verifier import MembershipInfo


class OrganizationMembershipVerifier:
    """Organizations module implementation of the tenancy platform MembershipVerifier protocol (§5.5).

    Queries the organizations application layer to retrieve membership details
    and packages them into a tenancy platform MembershipInfo DTO.
    """

    def get_membership(self, *, user_id: UUID, organization_id: UUID) -> MembershipInfo | None:
        result = get_membership_query(organization_id=organization_id, user_id=user_id)
        if result is None:
            return None

        return MembershipInfo(
            organization_id=result.organization_id,
            user_id=result.user_id,
            role=result.role,
            status=result.status,
            is_active=result.is_active,
        )
