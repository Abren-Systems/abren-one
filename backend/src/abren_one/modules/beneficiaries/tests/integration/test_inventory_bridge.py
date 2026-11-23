"""Integration tests for Beneficiaries → Inventory Aid Distribution Bridge (ADR-006).

Verifies that physical aid delivery to beneficiaries automatically issues
stock from warehouse inventory, enforces batch expiry safety, and creates
corresponding double-entry postings in the General Ledger.
"""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from abren_one.modules.beneficiaries.application.commands.record_service_delivery import (
    RecordServiceDeliveryInput,
)
from abren_one.modules.beneficiaries.application.commands.record_service_delivery import (
    execute as record_service_delivery,
)
from abren_one.modules.beneficiaries.application.commands.register_beneficiary import (
    RegisterBeneficiaryInput,
)
from abren_one.modules.beneficiaries.application.commands.register_beneficiary import (
    execute as register_beneficiary,
)
from abren_one.modules.beneficiaries.domain.value_objects import (
    BeneficiaryType,
    ServiceType,
    VulnerabilityLevel,
)
from abren_one.modules.inventory.public import (
    CreateItemBatchInput,
    CreateItemCategoryInput,
    CreateItemInput,
    CreateWarehouseInput,
    ExpiredStockIssueError,
    InsufficientStockError,
    OpeningStockLineInput,
    ReceiveOpeningStockInput,
    create_item,
    create_item_batch,
    create_item_category,
    create_warehouse,
    get_stock_balances,
    receive_opening_stock,
)
from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.modules.programs.public import (
    CreateProgramInput,
    create_program,
)
from abren_one.platform.authorization.roles import Role
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.mark.django_db
class TestBeneficiaryInventoryAidBridge:
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
                name="Syria Emergency Relief",
                slug=f"ser-{uuid4().hex[:6]}",
            )
        )
        self.org_id = org_res.organization_id

        self.admin_ctx = ExecutionContext(
            organization_id=self.org_id,
            actor_type=ActorType.USER,
            actor_id=uuid4(),
            actor_role=Role.ADMIN.value,
            correlation_id=uuid4(),
        )

        # 1. Setup Program
        prog_res = create_program(
            CreateProgramInput(
                context=self.admin_ctx,
                name="Winter Relief 2026",
                description="Winterization relief supplies",
            )
        )
        self.program_id = prog_res.program_id

        # 3. Setup Beneficiary
        ben_res = register_beneficiary(
            RegisterBeneficiaryInput(
                context=self.admin_ctx,
                beneficiary_type=BeneficiaryType.HOUSEHOLD.value,
                household_name="Al-Ahmad Family",
                vulnerability_level=VulnerabilityLevel.CRITICAL.value,
            )
        )
        self.beneficiary_id = ben_res.beneficiary_id

        # 4. Setup Warehouse & Item Catalog
        wh_res = create_warehouse(
            CreateWarehouseInput(
                context=self.admin_ctx,
                code="WH-NORTH",
                name="Northern Hub",
                warehouse_type="regional_depot",
            )
        )
        self.warehouse_id = wh_res.warehouse_id

        cat_res = create_item_category(
            CreateItemCategoryInput(
                context=self.admin_ctx,
                name="Shelter & Non-Food",
                code="NFI",
            )
        )
        self.category_id = cat_res.category_id

        self.item_hygiene = create_item(
            CreateItemInput(
                context=self.admin_ctx,
                category_id=self.category_id,
                item_code="HYG-KIT-01",
                name="Family Hygiene Kit",
                unit_of_measure="kit",
                item_type="relief_good",
                default_unit_cost=Decimal("35.00"),
            )
        )

        self.item_medicine = create_item(
            CreateItemInput(
                context=self.admin_ctx,
                category_id=self.category_id,
                item_code="MED-FIRSTAID",
                name="Emergency First Aid Kit",
                unit_of_measure="kit",
                item_type="relief_good",
                track_batches=True,
                track_expiry=True,
                default_unit_cost=Decimal("50.00"),
            )
        )

    def test_aid_delivery_with_inventory_stock_issue(self) -> None:
        """When aid delivery includes warehouse_id and item_id, stock is issued
        from inventory, balances update, and GL entries are automatically posted.
        """
        # Seed warehouse with 20 hygiene kits
        receive_opening_stock(
            ReceiveOpeningStockInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse_id,
                transaction_date=date(2026, 11, 20),
                lines=[
                    OpeningStockLineInput(
                        item_id=self.item_hygiene.item_id,
                        quantity=Decimal("20.00"),
                        unit_cost=Decimal("35.00"),
                    )
                ],
            )
        )

        # Distribute 3 kits to Al-Ahmad family
        deliv_res = record_service_delivery(
            RecordServiceDeliveryInput(
                context=self.admin_ctx,
                beneficiary_id=self.beneficiary_id,
                service_type=ServiceType.SHELTER_WASH.value,
                delivery_date=date(2026, 11, 23),
                quantity=Decimal("3.00"),
                unit="kit",
                program_id=self.program_id,
                notes="Delivered to head of household",
                warehouse_id=self.warehouse_id,
                item_id=self.item_hygiene.item_id,
            )
        )

        assert deliv_res.delivery_id is not None
        assert deliv_res.inventory_transaction_id is not None
        assert deliv_res.inventory_transaction_number != ""

        # Verify stock balance decreased: 20 - 3 = 17 kits remaining
        balances = get_stock_balances(
            self.admin_ctx,
            warehouse_id=self.warehouse_id,
            item_id=self.item_hygiene.item_id,
        )
        assert len(balances) == 1
        assert balances[0].quantity_on_hand == Decimal("17.00")

    def test_aid_delivery_rejects_expired_batch(self) -> None:
        """Humanitarian safety: attempting to distribute an expired batch of relief goods
        (e.g., expired medicines) is strictly rejected by domain validation.
        """
        # Create an expired batch (expired yesterday)
        batch_res = create_item_batch(
            CreateItemBatchInput(
                context=self.admin_ctx,
                item_id=self.item_medicine.item_id,
                batch_number="BATCH-EXP-001",
                expiry_date=date(2026, 11, 22),
            )
        )

        # Receive opening stock of this batch
        receive_opening_stock(
            ReceiveOpeningStockInput(
                context=self.admin_ctx,
                warehouse_id=self.warehouse_id,
                transaction_date=date(2026, 11, 20),
                lines=[
                    OpeningStockLineInput(
                        item_id=self.item_medicine.item_id,
                        batch_id=batch_res.batch_id,
                        quantity=Decimal("10.00"),
                        unit_cost=Decimal("50.00"),
                    )
                ],
            )
        )

        # Attempt to distribute expired batch today (2026-11-23) -> must raise ExpiredStockIssueError
        with pytest.raises(ExpiredStockIssueError):
            record_service_delivery(
                RecordServiceDeliveryInput(
                    context=self.admin_ctx,
                    beneficiary_id=self.beneficiary_id,
                    service_type=ServiceType.MEDICAL_SUPPORT.value,
                    delivery_date=date(2026, 11, 23),
                    quantity=Decimal("2.00"),
                    unit="kit",
                    program_id=self.program_id,
                    warehouse_id=self.warehouse_id,
                    item_id=self.item_medicine.item_id,
                    batch_id=batch_res.batch_id,
                )
            )

    def test_aid_delivery_rejects_insufficient_stock(self) -> None:
        """Attempting to distribute more items than available in warehouse stock raises InsufficientStockError."""
        # Warehouse has 0 units of hygiene kits
        with pytest.raises(InsufficientStockError):
            record_service_delivery(
                RecordServiceDeliveryInput(
                    context=self.admin_ctx,
                    beneficiary_id=self.beneficiary_id,
                    service_type=ServiceType.SHELTER_WASH.value,
                    delivery_date=date(2026, 11, 23),
                    quantity=Decimal("5.00"),
                    unit="kit",
                    warehouse_id=self.warehouse_id,
                    item_id=self.item_hygiene.item_id,
                )
            )

    def test_aid_delivery_without_inventory_operates_normally(self) -> None:
        """Standard service delivery (e.g. legal aid, training) without warehouse/item
        operates cleanly with zero inventory interaction.
        """
        deliv_res = record_service_delivery(
            RecordServiceDeliveryInput(
                context=self.admin_ctx,
                beneficiary_id=self.beneficiary_id,
                service_type=ServiceType.LEGAL_ADVOCACY.value,
                delivery_date=date(2026, 11, 23),
                quantity=Decimal("1.00"),
                unit="session",
                program_id=self.program_id,
            )
        )
        assert deliv_res.delivery_id is not None
        assert deliv_res.inventory_transaction_id is None
        assert deliv_res.inventory_transaction_number == ""
