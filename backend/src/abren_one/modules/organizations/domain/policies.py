"""Domain policies for the Organizations module.

Pure Python business rules governing organization and membership lifecycles.
Independent of ORM, database, and transport layers.
"""

from __future__ import annotations

from abren_one.modules.organizations.domain.value_objects import (
    MembershipRole,
    MembershipStatus,
    OrganizationStatus,
)

# Valid status transitions for organizations
_VALID_ORG_TRANSITIONS: dict[OrganizationStatus, set[OrganizationStatus]] = {
    OrganizationStatus.PROVISIONING: {OrganizationStatus.ACTIVE, OrganizationStatus.ARCHIVED},
    OrganizationStatus.ACTIVE: {OrganizationStatus.SUSPENDED, OrganizationStatus.ARCHIVED},
    OrganizationStatus.SUSPENDED: {OrganizationStatus.ACTIVE, OrganizationStatus.ARCHIVED},
    OrganizationStatus.ARCHIVED: set(),  # Terminal state
}

# Valid status transitions for memberships
_VALID_MEMBERSHIP_TRANSITIONS: dict[MembershipStatus, set[MembershipStatus]] = {
    MembershipStatus.INVITED: {MembershipStatus.ACTIVE, MembershipStatus.REVOKED},
    MembershipStatus.ACTIVE: {MembershipStatus.SUSPENDED, MembershipStatus.REVOKED},
    MembershipStatus.SUSPENDED: {MembershipStatus.ACTIVE, MembershipStatus.REVOKED},
    MembershipStatus.REVOKED: set(),  # Terminal state
}


def can_transition_org_status(current: OrganizationStatus, target: OrganizationStatus) -> bool:
    """Return True if the organization status transition is allowed."""
    if current == target:
        return True
    return target in _VALID_ORG_TRANSITIONS.get(current, set())


def can_transition_membership_status(current: MembershipStatus, target: MembershipStatus) -> bool:
    """Return True if the membership status transition is allowed."""
    if current == target:
        return True
    return target in _VALID_MEMBERSHIP_TRANSITIONS.get(current, set())


def can_revoke_membership(role: MembershipRole, total_active_owners: int) -> bool:
    """An organization must always have at least one active owner.

    Return False if revoking this membership would leave zero active owners.
    """
    return not (role == MembershipRole.OWNER and total_active_owners <= 1)


def is_membership_allowed_access(
    membership_status: MembershipStatus,
    org_status: OrganizationStatus,
) -> bool:
    """Check if the membership permits active operations in the organization.

    Both the organization and the membership must be active.
    """
    return membership_status == MembershipStatus.ACTIVE and org_status == OrganizationStatus.ACTIVE
