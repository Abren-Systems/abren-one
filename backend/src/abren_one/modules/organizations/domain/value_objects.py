from enum import StrEnum


class OrganizationStatus(StrEnum):
    """Lifecycle statuses for an organization (§5.2)."""

    PROVISIONING = "provisioning"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class MembershipStatus(StrEnum):
    """Lifecycle statuses for a user's membership in an organization (§5.2)."""

    INVITED = "invited"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class MembershipRole(StrEnum):
    """Roles a member can hold within an organization."""

    OWNER = "owner"
    ADMIN = "admin"
    STAFF = "staff"
    MEMBER = "member"
