from collections.abc import Callable
from typing import Any

from abren_one.platform.tenancy.context import (
    extract_organization_id,
    set_current_organization_id,
)
from abren_one.platform.tenancy.exceptions import TenantContextInvalidError


class TenantContextMiddleware:
    """Extracts tenant header if present and attaches to request (§5.5).

    Note: Per §5.5, middleware does NOT establish trusted tenant access.
    Trusted access is verified post-authentication by HasOrganizationContext.
    """

    def __init__(self, get_response: Callable[..., Any]) -> None:
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        try:
            org_id = extract_organization_id(request)
            request.requested_organization_id = org_id
            if org_id:
                set_current_organization_id(org_id)
        except TenantContextInvalidError:
            request.requested_organization_id = None

        try:
            response = self.get_response(request)
        finally:
            set_current_organization_id(None)

        return response
