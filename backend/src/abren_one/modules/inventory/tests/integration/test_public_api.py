from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from abren_one.modules.inventory.application.commands.create_item import (
    CreateItemInput,
)
from abren_one.modules.inventory.application.commands.create_item import (
    execute as create_item,
)
from abren_one.modules.inventory.application.commands.create_item_category import (
    CreateItemCategoryInput,
)
from abren_one.modules.inventory.application.commands.create_item_category import (
    execute as create_item_category,
)
from abren_one.modules.inventory.application.commands.create_warehouse import (
    CreateWarehouseInput,
)
from abren_one.modules.inventory.application.commands.create_warehouse import (
    execute as create_warehouse,
)
from abren_one.modules.inventory.application.commands.receive_opening_stock import (
    OpeningStockLineInput,
    ReceiveOpeningStockInput,
)
from abren_one.modules.inventory.application.commands.receive_opening_stock import (
    execute as receive_opening_stock,
)
from abren_one.modules.inventory.public import (
    ItemNotFoundError,
    check_item_availability,
    get_expiring_batches,
    get_reorder_alerts,
    get_stock_balances,
)
from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.platform.authorization.roles import Role
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.mark.django_db
class TestInventoryPublicInterface:
    @pytest.fixture(autouse=True)
    def setup_fixtures(self) -> None:
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid4(),
        )
        org_res = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Public API Test Org",
                slug=f"public-api-{uuid4().hex[:6]}",
            )
        )
        self.org_id = org_res.organization_id

        self.ctx = ExecutionContext(
            organization_id=self.org_id,
            actor_type=ActorType.USER,
            actor_id=uuid4(),
            actor_role=Role.ADMIN.value,
            correlation_id=uuid4(),
        )

        cat = create_item_category(CreateItemCategoryInput(context=self.ctx, name="Medical Supplies", code="MED"))
        item = create_item(
            CreateItemInput(
                context=self.ctx,
                category_id=cat.category_id,
                item_code="MED-BAND",
                name="Sterile Bandages",
                unit_of_measure="rolls",
                reorder_threshold=Decimal("30.00"),
            )
        )
        self.item_id = item.item_id

        wh = create_warehouse(CreateWarehouseInput(context=self.ctx, name="Main Warehouse", code="WH-MAIN"))
        self.wh_id = wh.warehouse_id

    def test_check_item_availability(self) -> None:
        """Availability returns correct sums and boolean status."""
        # Initial: 0 stock
        avail1 = check_item_availability(
            organization_id=self.org_id,
            item_id=self.item_id,
        )
        assert avail1.total_on_hand == Decimal("0.00")
        assert avail1.total_available == Decimal("0.00")
        assert not avail1.is_available

        # Receive stock
        receive_opening_stock(
            ReceiveOpeningStockInput(
                context=self.ctx,
                warehouse_id=self.wh_id,
                transaction_date=date(2026, 11, 20),
                lines=[OpeningStockLineInput(item_id=self.item_id, quantity=Decimal("75.00"))],
            )
        )

        # After receipt: 75 available
        avail2 = check_item_availability(
            organization_id=self.org_id,
            item_id=self.item_id,
        )
        assert avail2.total_on_hand == Decimal("75.00")
        assert avail2.total_available == Decimal("75.00")
        assert avail2.is_available

        # Non-existent item raises ItemNotFoundError
        with pytest.raises(ItemNotFoundError):
            check_item_availability(
                organization_id=self.org_id,
                item_id=uuid4(),
            )

    def test_public_queries_contract(self) -> None:
        """Public re-exported queries function identically to application queries."""
        receive_opening_stock(
            ReceiveOpeningStockInput(
                context=self.ctx,
                warehouse_id=self.wh_id,
                transaction_date=date(2026, 11, 20),
                lines=[OpeningStockLineInput(item_id=self.item_id, quantity=Decimal("20.00"))],
            )
        )

        balances = get_stock_balances(self.ctx, warehouse_id=self.wh_id)
        assert len(balances) == 1
        assert balances[0].item_id == self.item_id

        # Reorder threshold is 30, on hand is 20 -> alert
        alerts = get_reorder_alerts(self.ctx)
        assert len(alerts) == 1
        assert alerts[0].item_id == self.item_id

        # Expiring batches
        exp = get_expiring_batches(self.ctx)
        assert isinstance(exp, list)
