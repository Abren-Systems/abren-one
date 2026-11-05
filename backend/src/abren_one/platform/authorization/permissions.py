from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from abren_one.platform.authorization.evaluator import has_permission, has_role


def require_role(*allowed_roles: str) -> type[BasePermission]:
    """Factory creating a DRF permission class that requires one of the specified roles."""

    class RolePermission(BasePermission):
        message = f"Operation requires one of the following roles: {', '.join(allowed_roles)}"

        def has_permission(self, request: Request | Any, view: Any) -> bool:
            org_context = getattr(request, "org_context", None)
            if not org_context:
                return False
            return has_role(org_context.role, allowed_roles)

    return RolePermission


def require_permission(permission: str) -> type[BasePermission]:
    """Factory creating a DRF permission class that requires a specific permission."""

    class PermissionClass(BasePermission):
        message = f"Operation requires permission: '{permission}'"

        def has_permission(self, request: Request | Any, view: Any) -> bool:
            org_context = getattr(request, "org_context", None)
            if not org_context:
                return False
            return has_permission(org_context.role, permission)

    return PermissionClass
