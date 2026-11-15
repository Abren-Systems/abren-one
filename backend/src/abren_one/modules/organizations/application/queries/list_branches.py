from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.organizations.models import Branch


@dataclass(frozen=True)
class BranchSummaryResult:
    id: UUID
    organization_id: UUID
    name: str
    code: str
    is_headquarters: bool
    is_active: bool


def execute(*, organization_id: UUID) -> list[BranchSummaryResult]:
    """List all branches belonging to the organization."""
    branches = Branch.objects.filter(organization_id=organization_id).order_by("name")
    return [
        BranchSummaryResult(
            id=b.id,
            organization_id=b.organization_id,
            name=b.name,
            code=b.code,
            is_headquarters=b.is_headquarters,
            is_active=b.is_active,
        )
        for b in branches
    ]
