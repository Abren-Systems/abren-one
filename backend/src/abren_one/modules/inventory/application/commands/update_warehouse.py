from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.inventory.domain.exceptions import (
    InventoryError,
    WarehouseNotFoundError,
)
from abren_one.modules.inventory.domain.value_objects import WarehouseType
from abren_one.modules.inventory.models import Warehouse
from abren_one.modules.organizations.public import list_branches
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class UpdateWarehouseInput:
    context: ExecutionContext
    warehouse_id: UUID
    name: str | None = None
    warehouse_type: str | None = None
    branch_id: UUID | None = None
    custodian_id: UUID | None = None
    address: str | None = None
    is_active: bool | None = None


@dataclass(frozen=True)
class UpdateWarehouseResult:
    warehouse_id: UUID
    name: str
    code: str
    is_active: bool


@transaction.atomic
def execute(data: UpdateWarehouseInput) -> UpdateWarehouseResult:
    """Update details of a warehouse facility."""
    check_permission(data.context, "inventory:warehouses:manage")

    if data.context.organization_id is None:
        raise InventoryError("Organization context is required.")

    if data.context.actor_id is None:
        raise InventoryError("Actor ID is required.")

    try:
        warehouse = Warehouse.objects.select_for_update().get(
            id=data.warehouse_id,
            organization_id=data.context.organization_id,
        )
    except Warehouse.DoesNotExist as exc:
        raise WarehouseNotFoundError("Warehouse not found in this organization.") from exc

    if data.name is not None:
        name = data.name.strip()
        if not name:
            raise InventoryError("Warehouse name cannot be empty.")
        warehouse.name = name

    if data.warehouse_type is not None:
        valid_types = {t.value for t in WarehouseType}
        if data.warehouse_type not in valid_types:
            raise InventoryError(
                f"Invalid warehouse type '{data.warehouse_type}'. Must be one of {sorted(valid_types)}."
            )
        warehouse.warehouse_type = data.warehouse_type

    if data.branch_id is not None:
        org_branches = list_branches(organization_id=warehouse.organization_id)
        if not any(b.id == data.branch_id for b in org_branches):
            raise InventoryError("Referenced branch does not belong to this organization.")
        warehouse.branch_id = data.branch_id

    if data.custodian_id is not None:
        warehouse.custodian_id = data.custodian_id

    if data.address is not None:
        warehouse.address = data.address.strip()

    if data.is_active is not None:
        warehouse.is_active = data.is_active

    warehouse.save()

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=warehouse.organization_id,
        action="inventory.warehouse.updated",
        target_type="inventory.Warehouse",
        target_id=warehouse.id,
        correlation_id=data.context.correlation_id,
        metadata={"code": warehouse.code, "is_active": warehouse.is_active},
    )

    return UpdateWarehouseResult(
        warehouse_id=warehouse.id,
        name=warehouse.name,
        code=warehouse.code,
        is_active=warehouse.is_active,
    )
