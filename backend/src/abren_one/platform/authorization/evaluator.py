from collections.abc import Iterable

from django.core.exceptions import PermissionDenied

from abren_one.platform.authorization.roles import ROLE_PERMISSIONS, Role
from abren_one.platform.common.context import ActorType, ExecutionContext


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


def check_permission(context: ExecutionContext, permission: str) -> None:
    """Enforce permission at the application layer (§8.1, §8.4).

    Grants access unconditionally to ADMINISTRATOR and SYSTEM actors.
    For USER actors, checks whether context.actor_role possesses the permission.
    """
    if context.actor_type in (ActorType.ADMINISTRATOR, ActorType.SYSTEM):
        return
    if context.actor_role and has_permission(context.actor_role, permission):
        return
    raise PermissionDenied(f"Permission '{permission}' denied for role '{context.actor_role}'.")
