from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.organizations.models import Department


@dataclass(frozen=True)
class DepartmentSummaryResult:
    id: UUID
    organization_id: UUID
    branch_id: UUID | None
    name: str
    code: str
    is_active: bool


def execute(
    *,
    organization_id: UUID,
    branch_id: UUID | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[DepartmentSummaryResult]:
    """List departments for an organization, optionally filtered by branch."""
    qs = Department.objects.filter(organization_id=organization_id)
    if branch_id is not None:
        qs = qs.filter(branch_id=branch_id)
    qs = qs.order_by("name")[offset : offset + limit]

    return [
        DepartmentSummaryResult(
            id=d.id,
            organization_id=d.organization_id,
            branch_id=d.branch_id,
            name=d.name,
            code=d.code,
            is_active=d.is_active,
        )
        for d in qs
    ]
