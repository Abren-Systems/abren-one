from collections.abc import Iterable

from abren_one.platform.authorization.roles import ROLE_PERMISSIONS, Role


def has_role(actor_role: str | None, allowed_roles: Iterable[str]) -> bool:
    """Return True if actor_role matches any of the allowed_roles."""
    if not actor_role:
        return False
    return actor_role.lower() in {r.lower() for r in allowed_roles}


def has_permission(actor_role: str | None, permission: str) -> bool:
    """Return True if actor_role is granted the requested permission."""
    if not actor_role:
        return False
    # Owner has all permissions implicitly
    if actor_role.lower() == Role.OWNER.value:
        return True

    allowed_roles = ROLE_PERMISSIONS.get(permission, set())
    return actor_role.lower() in {r.lower() for r in allowed_roles}
