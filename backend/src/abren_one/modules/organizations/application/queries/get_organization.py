from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.organizations.domain.exceptions import OrganizationNotFoundError
from abren_one.modules.organizations.models import Organization


@dataclass(frozen=True)
class GetOrganizationResult:
    """Read DTO for organization details (§6.3)."""

    id: UUID
    name: str
    slug: str
    status: str
    is_active: bool


def execute(*, organization_id: UUID) -> GetOrganizationResult:
    """Retrieve an organization by ID."""
    try:
        org = Organization.objects.get(id=organization_id)
    except Organization.DoesNotExist as exc:
        raise OrganizationNotFoundError(f"Organization {organization_id} not found.") from exc

    return GetOrganizationResult(
        id=org.id,
        name=org.name,
        slug=org.slug,
        status=org.status,
        is_active=org.is_active,
    )
