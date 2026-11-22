from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.inventory.domain.exceptions import (
    InventoryError,
    WarehouseNotFoundError,
)
from abren_one.modules.inventory.models import Warehouse
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class LocationDto:
    id: UUID
    name: str
    code: str
    is_active: bool


@dataclass(frozen=True)
class WarehouseDetailResult:
    id: UUID
    name: str
    code: str
    warehouse_type: str
    branch_id: UUID | None
    custodian_id: UUID | None
    address: str
    is_active: bool
    locations: list[LocationDto]


def execute(context: ExecutionContext, warehouse_id: UUID) -> WarehouseDetailResult:
    """Retrieve detailed specification and internal storage locations for a warehouse."""
    if context.organization_id is None:
        raise InventoryError("Organization context is required.")

    try:
        warehouse = (
            Warehouse.objects.filter(
                id=warehouse_id,
                organization_id=context.organization_id,
            )
            .prefetch_related("locations")
            .get()
        )
    except Warehouse.DoesNotExist as exc:
        raise WarehouseNotFoundError("Warehouse not found in this organization.") from exc

    locations_dto = [
        LocationDto(
            id=loc.id,
            name=loc.name,
            code=loc.code,
            is_active=loc.is_active,
        )
        for loc in warehouse.locations.all().order_by("code")
    ]

    return WarehouseDetailResult(
        id=warehouse.id,
        name=warehouse.name,
        code=warehouse.code,
        warehouse_type=warehouse.warehouse_type,
        branch_id=warehouse.branch_id,
        custodian_id=warehouse.custodian_id,
        address=warehouse.address,
        is_active=warehouse.is_active,
        locations=locations_dto,
    )
