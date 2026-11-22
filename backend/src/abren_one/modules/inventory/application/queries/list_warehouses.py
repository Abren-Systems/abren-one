from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.inventory.domain.exceptions import InventoryError
from abren_one.modules.inventory.models import Warehouse
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class WarehouseSummaryResult:
    id: UUID
    name: str
    code: str
    warehouse_type: str
    branch_id: UUID | None
    custodian_id: UUID | None
    is_active: bool
    location_count: int


def execute(
    context: ExecutionContext,
    warehouse_type: str | None = None,
    is_active: bool | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[WarehouseSummaryResult]:
    """List warehouses for the active organization with bounded pagination."""
    if context.organization_id is None:
        raise InventoryError("Organization context is required.")

    qs = (
        Warehouse.objects.filter(organization_id=context.organization_id).prefetch_related("locations").order_by("name")
    )

    if warehouse_type:
        qs = qs.filter(warehouse_type=warehouse_type)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)

    return [
        WarehouseSummaryResult(
            id=wh.id,
            name=wh.name,
            code=wh.code,
            warehouse_type=wh.warehouse_type,
            branch_id=wh.branch_id,
            custodian_id=wh.custodian_id,
            is_active=wh.is_active,
            location_count=len(wh.locations.all()),
        )
        for wh in qs[offset : offset + limit]
    ]
