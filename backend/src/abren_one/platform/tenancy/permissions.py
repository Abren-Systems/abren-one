from __future__ import annotations

from typing import Any
from uuid import UUID

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from abren_one.platform.tenancy.context import (
    HEADER_ORGANIZATION_ID,
    OrganizationContext,
    extract_organization_id,
    set_current_organization_id,
)
from abren_one.platform.tenancy.exceptions import TenantContextInvalidError
from abren_one.platform.tenancy.verifier import verify_user_membership


class HasOrganizationContext(BasePermission):
    """Enforces active organization membership on tenant-scoped endpoints (§5.3, §5.5).

    Invariants checked:
    1. Caller is authenticated.
    2. X-Organization-ID header is present and valid UUID.
    3. Caller has an ACTIVE membership in the requested organization.

    Attaches `request.org_context: OrganizationContext` upon success.
    """

    message = "Active organization membership is required."

    def has_permission(self, request: Request | Any, view: Any) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        try:
            org_id: UUID | None = extract_organization_id(request)
        except TenantContextInvalidError as exc:
            raise PermissionDenied(str(exc)) from exc

        if org_id is None:
            raise PermissionDenied(f"The '{HEADER_ORGANIZATION_ID}' request header is required.")

        membership = verify_user_membership(user_id=user.id, organization_id=org_id)
        if membership is None or not membership.is_active:
            raise PermissionDenied("You do not have active membership in this organization.")

        request.org_context = OrganizationContext(
            organization_id=org_id,
            role=membership.role,
        )
        set_current_organization_id(org_id)
        return True
