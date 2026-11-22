from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.organizations.domain.exceptions import OrganizationError
from abren_one.modules.organizations.models import Branch, Organization
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateBranchInput:
    context: ExecutionContext
    name: str
    code: str
    is_headquarters: bool = False


@dataclass(frozen=True)
class CreateBranchResult:
    branch_id: UUID


@transaction.atomic
def execute(data: CreateBranchInput) -> CreateBranchResult:
    """Create a branch within the active organization (§5.3)."""
    check_permission(data.context, "organizations:manage")

    if data.context.organization_id is None:
        raise OrganizationError("Organization context is required.")

    org = Organization.objects.get(id=data.context.organization_id)
    if Branch.objects.filter(organization=org, code=data.code).exists():
        raise OrganizationError(f"Branch with code '{data.code}' already exists in this organization.")

    branch = Branch.objects.create(
        organization=org,
        name=data.name,
        code=data.code,
        is_headquarters=data.is_headquarters,
        is_active=True,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=org.id,
        action="branch.created",
        target_type="organizations.Branch",
        target_id=branch.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={"code": branch.code, "name": branch.name},
    )

    return CreateBranchResult(branch_id=branch.id)
