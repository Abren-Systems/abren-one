from enum import StrEnum


class Role(StrEnum):
    """Standard organizational roles evaluated by the platform (§8.1)."""

    OWNER = "owner"
    ADMIN = "admin"
    STAFF = "staff"
    MEMBER = "member"


# Mapping from permission name to set of roles that hold it
ROLE_PERMISSIONS: dict[str, set[str]] = {
    # Organizations permissions
    "organizations:view": {Role.OWNER, Role.ADMIN, Role.STAFF, Role.MEMBER},
    "organizations:manage": {Role.OWNER, Role.ADMIN},
    "members:view": {Role.OWNER, Role.ADMIN, Role.STAFF, Role.MEMBER},
    "members:invite": {Role.OWNER, Role.ADMIN},
    "members:manage": {Role.OWNER, Role.ADMIN},
    # Programs permissions
    "programs:view": {Role.OWNER, Role.ADMIN, Role.STAFF, Role.MEMBER},
    "programs:manage": {Role.OWNER, Role.ADMIN, Role.STAFF},
    "projects:manage": {Role.OWNER, Role.ADMIN, Role.STAFF},
    "activities:manage": {Role.OWNER, Role.ADMIN, Role.STAFF},
}
