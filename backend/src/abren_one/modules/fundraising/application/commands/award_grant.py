from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.fundraising.domain.exceptions import (
    FundraisingError,
    GrantNotFoundError,
)
from abren_one.modules.fundraising.domain.policies import validate_grant_transition
from abren_one.modules.fundraising.domain.value_objects import GrantStatus
from abren_one.modules.fundraising.models import Grant
from abren_one.modules.organizations.public import get_organization
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class AwardGrantInput:
    context: ExecutionContext
    grant_id: UUID
    notes: str = ""


@dataclass(frozen=True)
class AwardGrantResult:
    grant_id: UUID
    status: str


@transaction.atomic
def execute(data: AwardGrantInput) -> AwardGrantResult:
    """Transition a proposed grant to awarded status."""
    check_permission(data.context, "grants:manage")

    if data.context.organization_id is None:
        raise FundraisingError("Organization context is required.")
    org_id = data.context.organization_id

    org = get_organization(organization_id=org_id)
    if not org.is_active:
        raise FundraisingError("Cannot award a grant for an inactive or suspended organization.")

    grant = Grant.objects.select_for_update().filter(id=data.grant_id, organization_id=org.id).first()
    if not grant:
        raise GrantNotFoundError(f"Grant {data.grant_id} not found in this organization.")

    validate_grant_transition(grant.status, GrantStatus.AWARDED.value)

    grant.status = GrantStatus.AWARDED.value
    grant.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=org.id,
        action="fundraising.grant.awarded",
        target_type="fundraising.Grant",
        target_id=grant.id,
        correlation_id=data.context.correlation_id,
        outcome="success",
        metadata={
            "reference_code": grant.reference_code,
            "status": grant.status,
            "notes": data.notes,
        },
    )

    return AwardGrantResult(grant_id=grant.id, status=grant.status)
