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
    # Fundraising permissions
    "donors:view": {Role.OWNER, Role.ADMIN, Role.STAFF, Role.MEMBER},
    "donors:manage": {Role.OWNER, Role.ADMIN, Role.STAFF},
    "grants:view": {Role.OWNER, Role.ADMIN, Role.STAFF, Role.MEMBER},
    "grants:manage": {Role.OWNER, Role.ADMIN, Role.STAFF},
    "donations:view": {Role.OWNER, Role.ADMIN, Role.STAFF, Role.MEMBER},
    "donations:record": {Role.OWNER, Role.ADMIN, Role.STAFF},
    # Beneficiaries permissions
    "beneficiaries:view": {Role.OWNER, Role.ADMIN, Role.STAFF, Role.MEMBER},
    "beneficiaries:manage": {Role.OWNER, Role.ADMIN, Role.STAFF},
    "service_deliveries:view": {Role.OWNER, Role.ADMIN, Role.STAFF, Role.MEMBER},
    "service_deliveries:record": {Role.OWNER, Role.ADMIN, Role.STAFF},
    # Finance permissions
    "finance:accounts:view": {Role.OWNER, Role.ADMIN, Role.STAFF, Role.MEMBER},
    "finance:accounts:manage": {Role.OWNER, Role.ADMIN},
    "finance:journal_entries:view": {Role.OWNER, Role.ADMIN, Role.STAFF, Role.MEMBER},
    "finance:journal_entries:create": {Role.OWNER, Role.ADMIN, Role.STAFF},
    "finance:journal_entries:post": {Role.OWNER, Role.ADMIN},
    "finance:journal_entries:reverse": {Role.OWNER, Role.ADMIN},
    "finance:trial_balance:view": {Role.OWNER, Role.ADMIN, Role.STAFF, Role.MEMBER},
}
