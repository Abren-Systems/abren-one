import uuid
from datetime import date
from decimal import Decimal

import pytest

from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.modules.procurement.application.commands.approve_purchase_requisition import (
    ApprovePurchaseRequisitionInput,
)
from abren_one.modules.procurement.application.commands.approve_purchase_requisition import (
    execute as approve_purchase_requisition,
)
from abren_one.modules.procurement.application.commands.create_purchase_order import (
    CreateAllocationInput,
    CreatePurchaseOrderInput,
    CreatePurchaseOrderItemInput,
)
from abren_one.modules.procurement.application.commands.create_purchase_order import (
    execute as create_purchase_order,
)
from abren_one.modules.procurement.application.commands.create_purchase_requisition import (
    CreatePurchaseRequisitionInput,
    CreateRequisitionItemInput,
)
from abren_one.modules.procurement.application.commands.create_purchase_requisition import (
    execute as create_purchase_requisition,
)
from abren_one.modules.procurement.application.commands.create_vendor import (
    CreateVendorInput,
)
from abren_one.modules.procurement.application.commands.create_vendor import (
    execute as create_vendor,
)
from abren_one.modules.procurement.application.commands.inspect_goods_receipt import (
    InspectGoodsReceiptInput,
    InspectReceiptItemInput,
)
from abren_one.modules.procurement.application.commands.inspect_goods_receipt import (
    execute as inspect_goods_receipt,
)
from abren_one.modules.procurement.application.commands.issue_purchase_order import (
    IssuePurchaseOrderInput,
)
from abren_one.modules.procurement.application.commands.issue_purchase_order import (
    execute as issue_purchase_order,
)
from abren_one.modules.procurement.application.commands.record_goods_receipt import (
    RecordGoodsReceiptInput,
    RecordReceiptItemInput,
)
from abren_one.modules.procurement.application.commands.record_goods_receipt import (
    execute as record_goods_receipt,
)
from abren_one.modules.procurement.application.commands.submit_purchase_requisition import (
    SubmitPurchaseRequisitionInput,
)
from abren_one.modules.procurement.application.commands.submit_purchase_requisition import (
    execute as submit_purchase_requisition,
)
from abren_one.modules.procurement.application.queries.get_goods_receipt import (
    execute as get_goods_receipt,
)
from abren_one.modules.procurement.application.queries.get_order_delivery_position import (
    execute as get_order_delivery_position,
)
from abren_one.modules.procurement.application.queries.get_purchase_order import (
    execute as get_purchase_order,
)
from abren_one.modules.procurement.application.queries.get_purchase_requisition import (
    execute as get_purchase_requisition,
)
from abren_one.modules.procurement.application.queries.get_requisition_fulfillment import (
    execute as get_requisition_fulfillment,
)
from abren_one.modules.procurement.application.queries.get_vendor import (
    execute as get_vendor,
)
from abren_one.modules.procurement.application.queries.list_vendors import (
    execute as list_vendors,
)
from abren_one.modules.procurement.domain.value_objects import (
    VendorType,
)
from abren_one.modules.procurement.models import PurchaseOrder
from abren_one.modules.procurement.public import (
    get_accepted_receipts_for_order,
    get_commitment_detail,
    get_outstanding_commitments,
    get_unmatched_accepted_receipts,
)
from abren_one.modules.programs.public import (
    CreateProgramInput,
    create_program,
)
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.fixture
def org_context() -> tuple[uuid.UUID, ExecutionContext]:
    actor_id = uuid.uuid4()
    corr_id = uuid.uuid4()
    init_ctx = ExecutionContext(
        actor_type=ActorType.SYSTEM,
        actor_id=None,
        organization_id=None,
        correlation_id=corr_id,
    )
    org_res = create_organization(
        CreateOrganizationInput(
            context=init_ctx,
            name=f"Procurement Test Org {uuid.uuid4().hex[:6]}",
            slug=f"proc-test-org-{uuid.uuid4().hex[:6]}",
        )
    )
    ctx = ExecutionContext(
        actor_type=ActorType.USER,
        actor_id=actor_id,
        organization_id=org_res.organization_id,
        correlation_id=corr_id,
        actor_role="admin",
    )
    return org_res.organization_id, ctx


@pytest.mark.django_db
class TestProcurementQueries:
    def test_vendor_queries(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        v1 = create_vendor(
            CreateVendorInput(
                context=ctx,
                name="Alpha Logistics",
                vendor_type=VendorType.SERVICES.value,
                default_currency="USD",
            )
        )
        create_vendor(
            CreateVendorInput(
                context=ctx,
                name="Beta Books",
                default_currency="EUR",
            )
        )

        all_vendors = list_vendors(ctx)
        assert len(all_vendors) == 2

        service_vendors = list_vendors(ctx, vendor_type=VendorType.SERVICES.value)
        assert len(service_vendors) == 1
        assert service_vendors[0].name == "Alpha Logistics"

        v1_detail = get_vendor(ctx, v1.vendor_id)
        assert v1_detail.name == "Alpha Logistics"
        assert v1_detail.vendor_type == VendorType.SERVICES.value

    def test_requisition_and_fulfillment_queries(
        self,
        org_context: tuple[uuid.UUID, ExecutionContext],
    ):
        org_id, ctx = org_context
        # Create program
        prog = create_program(
            CreateProgramInput(
                context=ctx,
                name="Education Initiative",
                description="School supplies",
            )
        )

        # Create vendor
        v_res = create_vendor(CreateVendorInput(context=ctx, name="Stationery Pro"))

        # Create Requisition with 2 items
        req_res = create_purchase_requisition(
            CreatePurchaseRequisitionInput(
                context=ctx,
                title="School Supplies 2026",
                items=[
                    CreateRequisitionItemInput(
                        description="Notebooks",
                        quantity=Decimal("100"),
                        unit="pcs",
                        estimated_unit_price=Decimal("3.00"),
                        program_id=prog.program_id,
                    ),
                    CreateRequisitionItemInput(
                        description="Pencils",
                        quantity=Decimal("200"),
                        unit="pcs",
                        estimated_unit_price=Decimal("0.50"),
                        program_id=prog.program_id,
                    ),
                ],
            )
        )

        # Before order: fulfillment is NOT_ORDERED
        fulf_0 = get_requisition_fulfillment(ctx, req_res.requisition_id)
        assert fulf_0.fulfillment_position == "NOT_ORDERED"
        nb_dto = next(it for it in fulf_0.items if it.description == "Notebooks")
        assert nb_dto.quantity_outstanding_order == Decimal("100.00")

        # Submit and approve requisition
        submit_purchase_requisition(SubmitPurchaseRequisitionInput(context=ctx, requisition_id=req_res.requisition_id))
        approver_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org_id,
            correlation_id=uuid.uuid4(),
            actor_role="owner",
        )
        approve_purchase_requisition(
            ApprovePurchaseRequisitionInput(
                context=approver_ctx,
                requisition_id=req_res.requisition_id,
            )
        )

        req_detail = get_purchase_requisition(ctx, req_res.requisition_id)
        notebook_item_id = next(i.id for i in req_detail.items if i.description == "Notebooks")
        pencil_item_id = next(i.id for i in req_detail.items if i.description == "Pencils")

        # Order only notebooks (100) -> PARTIALLY_ORDERED
        po_res = create_purchase_order(
            CreatePurchaseOrderInput(
                context=ctx,
                vendor_id=v_res.vendor_id,
                requisition_id=req_res.requisition_id,
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Notebooks",
                        quantity=Decimal("100"),
                        unit="pcs",
                        unit_price=Decimal("2.90"),
                        allocations=[
                            CreateAllocationInput(
                                requisition_item_id=notebook_item_id,
                                allocated_quantity=Decimal("100"),
                            )
                        ],
                    )
                ],
            )
        )

        fulf_1 = get_requisition_fulfillment(ctx, req_res.requisition_id)
        assert fulf_1.fulfillment_position == "PARTIALLY_ORDERED"

        # Order remaining pencils (200) -> FULLY_ORDERED
        create_purchase_order(
            CreatePurchaseOrderInput(
                context=ctx,
                vendor_id=v_res.vendor_id,
                requisition_id=req_res.requisition_id,
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Pencils",
                        quantity=Decimal("200"),
                        unit="pcs",
                        unit_price=Decimal("0.45"),
                        allocations=[
                            CreateAllocationInput(
                                requisition_item_id=pencil_item_id,
                                allocated_quantity=Decimal("200"),
                            )
                        ],
                    )
                ],
            )
        )

        fulf_2 = get_requisition_fulfillment(ctx, req_res.requisition_id)
        assert fulf_2.fulfillment_position == "FULLY_ORDERED"

        # Issue the first PO and receive notebooks
        issue_purchase_order(IssuePurchaseOrderInput(context=ctx, order_id=po_res.order_id))
        po_detail = get_purchase_order(ctx, po_res.order_id)
        po_item_id = po_detail.items[0].id

        grn_res = record_goods_receipt(
            RecordGoodsReceiptInput(
                context=ctx,
                purchase_order_id=po_res.order_id,
                received_date=date.today(),
                items=[
                    RecordReceiptItemInput(
                        po_item_id=po_item_id,
                        quantity_received=Decimal("100"),
                    )
                ],
            )
        )
        grn_detail = get_goods_receipt(ctx, grn_res.receipt_id)
        grn_item_id = grn_detail.items[0].id

        # Inspect 100 accepted
        inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=ctx,
                receipt_id=grn_res.receipt_id,
                inspections=[
                    InspectReceiptItemInput(
                        grn_item_id=grn_item_id,
                        quantity_accepted=Decimal("100"),
                        quantity_rejected=Decimal("0"),
                    )
                ],
            )
        )

        # Now notebooks accepted (100) but pencils not yet accepted (0/200) -> PARTIALLY_FULFILLED
        fulf_3 = get_requisition_fulfillment(ctx, req_res.requisition_id)
        assert fulf_3.fulfillment_position == "PARTIALLY_FULFILLED"

    def test_order_delivery_position_query(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        v_res = create_vendor(CreateVendorInput(context=ctx, name="Tech Devices Ltd"))
        po_res = create_purchase_order(
            CreatePurchaseOrderInput(
                context=ctx,
                vendor_id=v_res.vendor_id,
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Tablets",
                        quantity=Decimal("10"),
                        unit="pcs",
                        unit_price=Decimal("200.00"),
                    )
                ],
            )
        )

        # NOT_DELIVERED initially
        pos_0 = get_order_delivery_position(ctx, po_res.order_id)
        assert pos_0.delivery_position == "NOT_DELIVERED"

        issue_purchase_order(IssuePurchaseOrderInput(context=ctx, order_id=po_res.order_id))
        po = PurchaseOrder.objects.get(id=po_res.order_id)
        po_item = po.items.first()
        assert po_item is not None

        # Receive 5 tablets and inspect (5 accepted) -> PARTIALLY_DELIVERED
        grn1 = record_goods_receipt(
            RecordGoodsReceiptInput(
                context=ctx,
                purchase_order_id=po.id,
                received_date=date.today(),
                items=[
                    RecordReceiptItemInput(
                        po_item_id=po_item.id,
                        quantity_received=Decimal("5"),
                    )
                ],
            )
        )
        inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=ctx,
                receipt_id=grn1.receipt_id,
                inspections=[
                    InspectReceiptItemInput(
                        grn_item_id=grn1.receipt_id,  # will fetch first item
                        quantity_accepted=Decimal("5"),
                        quantity_rejected=Decimal("0"),
                    )
                ],
            )
        ) if False else None  # let's do proper item lookup

        grn1_obj = get_goods_receipt(ctx, grn1.receipt_id)
        inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=ctx,
                receipt_id=grn1.receipt_id,
                inspections=[
                    InspectReceiptItemInput(
                        grn_item_id=grn1_obj.items[0].id,
                        quantity_accepted=Decimal("5"),
                        quantity_rejected=Decimal("0"),
                    )
                ],
            )
        )

        pos_1 = get_order_delivery_position(ctx, po_res.order_id)
        assert pos_1.delivery_position == "PARTIALLY_DELIVERED"
        assert pos_1.items[0].quantity_accepted == Decimal("5.00")
        assert pos_1.items[0].quantity_outstanding == Decimal("5.00")

        # Receive remaining 5 tablets and inspect (5 accepted) -> FULLY_DELIVERED
        grn2 = record_goods_receipt(
            RecordGoodsReceiptInput(
                context=ctx,
                purchase_order_id=po.id,
                received_date=date.today(),
                items=[
                    RecordReceiptItemInput(
                        po_item_id=po_item.id,
                        quantity_received=Decimal("5"),
                    )
                ],
            )
        )
        grn2_obj = get_goods_receipt(ctx, grn2.receipt_id)
        inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=ctx,
                receipt_id=grn2.receipt_id,
                inspections=[
                    InspectReceiptItemInput(
                        grn_item_id=grn2_obj.items[0].id,
                        quantity_accepted=Decimal("5"),
                        quantity_rejected=Decimal("0"),
                    )
                ],
            )
        )

        pos_2 = get_order_delivery_position(ctx, po_res.order_id)
        assert pos_2.delivery_position == "FULLY_DELIVERED"
        assert pos_2.items[0].quantity_outstanding == Decimal("0.00")

        # Over-delivery: receive 2 additional bonus tablets and accept them
        grn3 = record_goods_receipt(
            RecordGoodsReceiptInput(
                context=ctx,
                purchase_order_id=po.id,
                received_date=date.today(),
                items=[
                    RecordReceiptItemInput(
                        po_item_id=po_item.id,
                        quantity_received=Decimal("2"),
                    )
                ],
            )
        )
        grn3_obj = get_goods_receipt(ctx, grn3.receipt_id)
        inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=ctx,
                receipt_id=grn3.receipt_id,
                inspections=[
                    InspectReceiptItemInput(
                        grn_item_id=grn3_obj.items[0].id,
                        quantity_accepted=Decimal("2"),
                        quantity_rejected=Decimal("0"),
                    )
                ],
            )
        )
        pos_3 = get_order_delivery_position(ctx, po_res.order_id)
        assert pos_3.delivery_position == "OVER_DELIVERED"
        assert pos_3.items[0].quantity_accepted == Decimal("12.00")

    def test_multi_vendor_partial_fulfillment_lifecycle(
        self,
        org_context: tuple[uuid.UUID, ExecutionContext],
    ):
        """IMP-2: 1 Requisition split across 2 Vendors/POs progressing through full fulfillment."""
        org_id, ctx = org_context
        vendor_a = create_vendor(CreateVendorInput(context=ctx, name="Vendor A (Books)"))
        vendor_b = create_vendor(CreateVendorInput(context=ctx, name="Vendor B (Pens)"))

        # PR with 500 Books and 300 Pens
        req = create_purchase_requisition(
            CreatePurchaseRequisitionInput(
                context=ctx,
                title="Consolidated School Order",
                items=[
                    CreateRequisitionItemInput(
                        description="Exercise Books",
                        quantity=Decimal("500"),
                        unit="books",
                        estimated_unit_price=Decimal("2.00"),
                    ),
                    CreateRequisitionItemInput(
                        description="Ballpoint Pens",
                        quantity=Decimal("300"),
                        unit="pens",
                        estimated_unit_price=Decimal("0.50"),
                    ),
                ],
            )
        )
        submit_purchase_requisition(SubmitPurchaseRequisitionInput(context=ctx, requisition_id=req.requisition_id))
        approver_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org_id,
            correlation_id=uuid.uuid4(),
            actor_role="owner",
        )
        approve_purchase_requisition(
            ApprovePurchaseRequisitionInput(
                context=approver_ctx,
                requisition_id=req.requisition_id,
            )
        )

        req_detail = get_purchase_requisition(ctx, req.requisition_id)
        book_item = next(i for i in req_detail.items if i.description == "Exercise Books")
        pen_item = next(i for i in req_detail.items if i.description == "Ballpoint Pens")

        # 1. State: NOT_ORDERED
        f0 = get_requisition_fulfillment(ctx, req.requisition_id)
        assert f0.fulfillment_position == "NOT_ORDERED"

        # 2. PO 1 with Vendor A for Exercise Books only -> PARTIALLY_ORDERED
        po1 = create_purchase_order(
            CreatePurchaseOrderInput(
                context=ctx,
                vendor_id=vendor_a.vendor_id,
                requisition_id=req.requisition_id,
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Exercise Books",
                        quantity=Decimal("500"),
                        unit="books",
                        unit_price=Decimal("1.95"),
                        allocations=[
                            CreateAllocationInput(
                                requisition_item_id=book_item.id,
                                allocated_quantity=Decimal("500"),
                            )
                        ],
                    )
                ],
            )
        )
        f1 = get_requisition_fulfillment(ctx, req.requisition_id)
        assert f1.fulfillment_position == "PARTIALLY_ORDERED"

        # 3. PO 2 with Vendor B for Pens -> FULLY_ORDERED
        po2 = create_purchase_order(
            CreatePurchaseOrderInput(
                context=ctx,
                vendor_id=vendor_b.vendor_id,
                requisition_id=req.requisition_id,
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Ballpoint Pens",
                        quantity=Decimal("300"),
                        unit="pens",
                        unit_price=Decimal("0.48"),
                        allocations=[
                            CreateAllocationInput(
                                requisition_item_id=pen_item.id,
                                allocated_quantity=Decimal("300"),
                            )
                        ],
                    )
                ],
            )
        )
        f2 = get_requisition_fulfillment(ctx, req.requisition_id)
        assert f2.fulfillment_position == "FULLY_ORDERED"

        # 4. Deliver and inspect PO 1 (Books) -> PARTIALLY_FULFILLED
        issue_purchase_order(IssuePurchaseOrderInput(context=ctx, order_id=po1.order_id))
        po1_detail = get_purchase_order(ctx, po1.order_id)
        grn1 = record_goods_receipt(
            RecordGoodsReceiptInput(
                context=ctx,
                purchase_order_id=po1.order_id,
                received_date=date.today(),
                items=[
                    RecordReceiptItemInput(
                        po_item_id=po1_detail.items[0].id,
                        quantity_received=Decimal("500"),
                    )
                ],
            )
        )
        grn1_detail = get_goods_receipt(ctx, grn1.receipt_id)
        inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=ctx,
                receipt_id=grn1.receipt_id,
                inspections=[
                    InspectReceiptItemInput(
                        grn_item_id=grn1_detail.items[0].id,
                        quantity_accepted=Decimal("500"),
                        quantity_rejected=Decimal("0"),
                    )
                ],
            )
        )
        f3 = get_requisition_fulfillment(ctx, req.requisition_id)
        assert f3.fulfillment_position == "PARTIALLY_FULFILLED"

        # 5. Deliver and inspect PO 2 (Pens) -> FULLY_FULFILLED
        issue_purchase_order(IssuePurchaseOrderInput(context=ctx, order_id=po2.order_id))
        po2_detail = get_purchase_order(ctx, po2.order_id)
        grn2 = record_goods_receipt(
            RecordGoodsReceiptInput(
                context=ctx,
                purchase_order_id=po2.order_id,
                received_date=date.today(),
                items=[
                    RecordReceiptItemInput(
                        po_item_id=po2_detail.items[0].id,
                        quantity_received=Decimal("300"),
                    )
                ],
            )
        )
        grn2_detail = get_goods_receipt(ctx, grn2.receipt_id)
        inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=ctx,
                receipt_id=grn2.receipt_id,
                inspections=[
                    InspectReceiptItemInput(
                        grn_item_id=grn2_detail.items[0].id,
                        quantity_accepted=Decimal("300"),
                        quantity_rejected=Decimal("0"),
                    )
                ],
            )
        )
        f4 = get_requisition_fulfillment(ctx, req.requisition_id)
        assert f4.fulfillment_position == "FULLY_FULFILLED"


@pytest.mark.django_db
class TestPublicInterface:
    """Validate cross-module financial integration contracts exposed via public.py."""

    def test_commitment_and_receipt_queries(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        org_id, ctx = org_context
        prog = create_program(
            CreateProgramInput(
                context=ctx,
                name="Health Camp",
                description="Mobile medical clinic",
            )
        )
        vendor = create_vendor(
            CreateVendorInput(
                context=ctx,
                name="MedPharma International",
                default_payment_terms="Net 30",
            )
        )

        # Create Requisition
        req = create_purchase_requisition(
            CreatePurchaseRequisitionInput(
                context=ctx,
                title="Vaccines & Syringes",
                items=[
                    CreateRequisitionItemInput(
                        description="Syringes 100pk",
                        quantity=Decimal("50"),
                        unit="packs",
                        estimated_unit_price=Decimal("10.00"),
                        program_id=prog.program_id,
                    )
                ],
            )
        )
        submit_purchase_requisition(SubmitPurchaseRequisitionInput(context=ctx, requisition_id=req.requisition_id))
        approver_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org_id,
            correlation_id=uuid.uuid4(),
            actor_role="owner",
        )
        approve_purchase_requisition(
            ApprovePurchaseRequisitionInput(
                context=approver_ctx,
                requisition_id=req.requisition_id,
            )
        )

        req_detail = get_purchase_requisition(ctx, req.requisition_id)
        req_item_id = req_detail.items[0].id

        # Create and issue PO
        po = create_purchase_order(
            CreatePurchaseOrderInput(
                context=ctx,
                vendor_id=vendor.vendor_id,
                requisition_id=req.requisition_id,
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Syringes 100pk",
                        quantity=Decimal("50"),
                        unit="packs",
                        unit_price=Decimal("9.50"),
                        allocations=[
                            CreateAllocationInput(
                                requisition_item_id=req_item_id,
                                allocated_quantity=Decimal("50"),
                            )
                        ],
                    )
                ],
            )
        )
        issue_purchase_order(IssuePurchaseOrderInput(context=ctx, order_id=po.order_id))

        # Check outstanding commitments via public API
        commitments = get_outstanding_commitments(org_id, program_id=prog.program_id)
        assert len(commitments) == 1
        summary = commitments[0]
        assert summary.order_number == po.order_number
        assert summary.vendor_name == "MedPharma International"
        assert summary.total_committed == Decimal("475.00")  # 50 * 9.50
        assert summary.total_delivered == Decimal("0.00")
        assert summary.total_outstanding == Decimal("475.00")
        assert summary.items[0].program_id == prog.program_id

        # Detail query via public API
        detail = get_commitment_detail(org_id, po.order_id)
        assert detail.po_id == po.order_id
        assert detail.total_committed == Decimal("475.00")

        # Deliver and accept 30 syringes
        po_obj = PurchaseOrder.objects.get(id=po.order_id)
        po_item_obj = po_obj.items.first()
        assert po_item_obj is not None

        grn = record_goods_receipt(
            RecordGoodsReceiptInput(
                context=ctx,
                purchase_order_id=po.order_id,
                received_date=date.today(),
                items=[
                    RecordReceiptItemInput(
                        po_item_id=po_item_obj.id,
                        quantity_received=Decimal("30"),
                    )
                ],
            )
        )
        grn_detail = get_goods_receipt(ctx, grn.receipt_id)
        inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=ctx,
                receipt_id=grn.receipt_id,
                inspections=[
                    InspectReceiptItemInput(
                        grn_item_id=grn_detail.items[0].id,
                        quantity_accepted=Decimal("30"),
                        quantity_rejected=Decimal("0"),
                    )
                ],
            )
        )

        # Check accepted receipts for order via public API
        accepted_receipts = get_accepted_receipts_for_order(org_id, po.order_id)
        assert len(accepted_receipts) == 1
        assert accepted_receipts[0].quantity_accepted == Decimal("30.00")
        assert accepted_receipts[0].accepted_value == Decimal("285.00")  # 30 * 9.50
        assert accepted_receipts[0].program_id == prog.program_id

        # Check unmatched receipts via public API
        unmatched = get_unmatched_accepted_receipts(org_id)
        assert len(unmatched) >= 1
        assert unmatched[0].receipt_number == grn.receipt_number

        # Check updated commitment summary
        updated_detail = get_commitment_detail(org_id, po.order_id)
        assert updated_detail.total_committed == Decimal("475.00")
        assert updated_detail.total_delivered == Decimal("285.00")
        assert updated_detail.total_outstanding == Decimal("190.00")  # 475 - 285
