from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.inventory.domain.exceptions import (
    InventoryError,
)
from abren_one.modules.inventory.domain.value_objects import WarehouseType
from abren_one.modules.inventory.models import Warehouse
from abren_one.modules.organizations.public import get_organization, list_branches
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateWarehouseInput:
    context: ExecutionContext
    name: str
    code: str
    warehouse_type: str = WarehouseType.REGIONAL_DEPOT.value
    branch_id: UUID | None = None
    custodian_id: UUID | None = None
    address: str = ""


@dataclass(frozen=True)
class CreateWarehouseResult:
    warehouse_id: UUID
    name: str
    code: str
    warehouse_type: str
    is_active: bool


@transaction.atomic
def execute(data: CreateWarehouseInput) -> CreateWarehouseResult:
    """Provision a new warehouse facility for the organization."""
    check_permission(data.context, "inventory:warehouses:manage")

    if data.context.organization_id is None:
        raise InventoryError("Organization context is required.")

    if data.context.actor_id is None:
        raise InventoryError("Actor ID is required.")

    org = get_organization(organization_id=data.context.organization_id)
    if not org.is_active:
        raise InventoryError("Cannot create warehouse for an inactive organization.")

    name = data.name.strip()
    if not name:
        raise InventoryError("Warehouse name cannot be empty.")

    code = data.code.strip().upper()
    if not code:
        raise InventoryError("Warehouse code cannot be empty.")

    valid_types = {t.value for t in WarehouseType}
    if data.warehouse_type not in valid_types:
        raise InventoryError(f"Invalid warehouse type '{data.warehouse_type}'. Must be one of {sorted(valid_types)}.")

    if Warehouse.objects.filter(organization_id=org.id, code=code).exists():
        raise InventoryError(f"Warehouse with code '{code}' already exists in this organization.")

    # Soft reference cross-module verification for branch
    if data.branch_id is not None:
        org_branches = list_branches(organization_id=org.id)
        if not any(b.id == data.branch_id for b in org_branches):
            raise InventoryError("Referenced branch does not belong to this organization.")

    warehouse = Warehouse.objects.create(
        organization_id=org.id,
        name=name,
        code=code,
        warehouse_type=data.warehouse_type,
        branch_id=data.branch_id,
        custodian_id=data.custodian_id,
        address=data.address.strip(),
        is_active=True,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=org.id,
        action="inventory.warehouse.created",
        target_type="inventory.Warehouse",
        target_id=warehouse.id,
        correlation_id=data.context.correlation_id,
        metadata={
            "name": warehouse.name,
            "code": warehouse.code,
            "warehouse_type": warehouse.warehouse_type,
            "branch_id": str(data.branch_id) if data.branch_id else None,
        },
    )

    return CreateWarehouseResult(
        warehouse_id=warehouse.id,
        name=warehouse.name,
        code=warehouse.code,
        warehouse_type=warehouse.warehouse_type,
        is_active=warehouse.is_active,
    )
