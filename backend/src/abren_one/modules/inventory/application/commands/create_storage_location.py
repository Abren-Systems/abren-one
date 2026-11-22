from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.inventory.domain.exceptions import (
    InventoryError,
    WarehouseNotFoundError,
)
from abren_one.modules.inventory.models import StorageLocation, Warehouse
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateStorageLocationInput:
    context: ExecutionContext
    warehouse_id: UUID
    name: str
    code: str


@dataclass(frozen=True)
class CreateStorageLocationResult:
    location_id: UUID
    warehouse_id: UUID
    name: str
    code: str
    is_active: bool


@transaction.atomic
def execute(data: CreateStorageLocationInput) -> CreateStorageLocationResult:
    """Create a storage location/bin within a warehouse."""
    check_permission(data.context, "inventory:warehouses:manage")

    if data.context.organization_id is None:
        raise InventoryError("Organization context is required.")

    if data.context.actor_id is None:
        raise InventoryError("Actor ID is required.")

    try:
        warehouse = Warehouse.objects.get(
            id=data.warehouse_id,
            organization_id=data.context.organization_id,
        )
    except Warehouse.DoesNotExist as exc:
        raise WarehouseNotFoundError("Warehouse not found in this organization.") from exc

    name = data.name.strip()
    if not name:
        raise InventoryError("Storage location name cannot be empty.")

    code = data.code.strip().upper()
    if not code:
        raise InventoryError("Storage location code cannot be empty.")

    if StorageLocation.objects.filter(warehouse=warehouse, code=code).exists():
        raise InventoryError(f"Storage location with code '{code}' already exists in this warehouse.")

    location = StorageLocation.objects.create(
        warehouse=warehouse,
        name=name,
        code=code,
        is_active=True,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=warehouse.organization_id,
        action="inventory.storage_location.created",
        target_type="inventory.StorageLocation",
        target_id=location.id,
        correlation_id=data.context.correlation_id,
        metadata={"warehouse_code": warehouse.code, "location_code": location.code},
    )

    return CreateStorageLocationResult(
        location_id=location.id,
        warehouse_id=warehouse.id,
        name=location.name,
        code=location.code,
        is_active=location.is_active,
    )
