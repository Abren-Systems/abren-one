from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from abren_one.platform.tenancy.exceptions import TenantContextInvalidError

HEADER_ORGANIZATION_ID = "X-Organization-ID"
DJANGO_META_HEADER = "HTTP_X_ORGANIZATION_ID"

_current_org_id: ContextVar[UUID | None] = ContextVar("current_org_id", default=None)


@dataclass(frozen=True)
class OrganizationContext:
    """Resolved tenant context attached to an authenticated request (§5.5)."""

    organization_id: UUID
    role: str | None = None
    branch_id: UUID | None = None


def set_current_organization_id(org_id: UUID | None) -> None:
    """Set the active organization ID for the current context/thread."""
    _current_org_id.set(org_id)


def get_current_organization_id() -> UUID | None:
    """Get the active organization ID for the current context/thread."""
    return _current_org_id.get()


def extract_organization_id(request: Any) -> UUID | None:
    """Extract and validate the organization UUID from an HTTP request header.

    Returns None if the header is not present.
    Raises TenantContextInvalidError if the header is present but not a valid UUID.
    """
    raw_id: str | None = None

    # DRF / Django request headers mapping
    if hasattr(request, "headers") and HEADER_ORGANIZATION_ID in request.headers:
        raw_id = request.headers.get(HEADER_ORGANIZATION_ID)
    elif hasattr(request, "META") and DJANGO_META_HEADER in request.META:
        raw_id = request.META.get(DJANGO_META_HEADER)

    if not raw_id:
        return None

    try:
        return UUID(raw_id.strip())
    except (ValueError, AttributeError) as exc:
        raise TenantContextInvalidError(f"Malformed organization ID: {raw_id}") from exc
