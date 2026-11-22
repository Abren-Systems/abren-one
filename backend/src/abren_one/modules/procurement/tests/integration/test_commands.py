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
from abren_one.modules.procurement.application.commands.cancel_purchase_order import (
    CancelPurchaseOrderInput,
)
from abren_one.modules.procurement.application.commands.cancel_purchase_order import (
    execute as cancel_purchase_order,
)
from abren_one.modules.procurement.application.commands.close_purchase_order import (
    ClosePurchaseOrderInput,
)
from abren_one.modules.procurement.application.commands.close_purchase_order import (
    execute as close_purchase_order,
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
from abren_one.modules.procurement.application.commands.deactivate_vendor import (
    DeactivateVendorInput,
)
from abren_one.modules.procurement.application.commands.deactivate_vendor import (
    execute as deactivate_vendor,
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
from abren_one.modules.procurement.application.commands.reject_purchase_requisition import (
    RejectPurchaseRequisitionInput,
)
from abren_one.modules.procurement.application.commands.reject_purchase_requisition import (
    execute as reject_purchase_requisition,
)
from abren_one.modules.procurement.application.commands.return_requisition_to_draft import (
    ReturnRequisitionToDraftInput,
)
from abren_one.modules.procurement.application.commands.return_requisition_to_draft import (
    execute as return_requisition_to_draft,
)
from abren_one.modules.procurement.application.commands.submit_purchase_requisition import (
    SubmitPurchaseRequisitionInput,
)
from abren_one.modules.procurement.application.commands.submit_purchase_requisition import (
    execute as submit_purchase_requisition,
)
from abren_one.modules.procurement.application.commands.update_draft_requisition import (
    UpdateDraftRequisitionInput,
)
from abren_one.modules.procurement.application.commands.update_draft_requisition import (
    execute as update_draft_requisition,
)
from abren_one.modules.procurement.application.commands.update_vendor import (
    UpdateVendorInput,
)
from abren_one.modules.procurement.application.commands.update_vendor import (
    execute as update_vendor,
)
from abren_one.modules.procurement.domain.exceptions import (
    CancellationBlockedError,
    EmptyRequisitionError,
    InactiveVendorError,
    InspectionQuantityError,
    InvalidRequisitionTransitionError,
    OrganizationMismatchError,
    OverAllocationError,
    ProcurementError,
    SelfApprovalError,
)
from abren_one.modules.procurement.domain.value_objects import (
    AuthorizationStatus,
    PurchaseOrderStatus,
    ReceiptType,
    VendorType,
)
from abren_one.modules.procurement.models import (
    GoodsReceiptNote,
    PurchaseOrder,
    PurchaseRequisition,
    Vendor,
)
from abren_one.platform.audit.models import AuditEvent
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
            name=f"Relief NGO {uuid.uuid4().hex[:6]}",
            slug=f"relief-ngo-{uuid.uuid4().hex[:6]}",
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
class TestVendorCommands:
    def test_create_vendor_success(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        org_id, ctx = org_context
        res = create_vendor(
            CreateVendorInput(
                context=ctx,
                name="Acme Medical Supplies",
                vendor_type=VendorType.GOODS.value,
                tax_id="TAX-12345",
                country="ETH",
                contact_name="Abebe Bikila",
                email="contact@acme.et",
                default_payment_terms="Net 30",
            )
        )
        assert res.name == "Acme Medical Supplies"
        assert res.is_active is True
        vendor = Vendor.objects.get(id=res.vendor_id)
        assert vendor.organization_id == org_id
        assert vendor.tax_id == "TAX-12345"

        audit = AuditEvent.objects.filter(
            organization_id=org_id,
            action="procurement.vendor.created",
            target_id=res.vendor_id,
        ).first()
        assert audit is not None

    def test_duplicate_vendor_name_fails(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        create_vendor(CreateVendorInput(context=ctx, name="Duplicate Vendor"))
        with pytest.raises(ProcurementError, match="already exists"):
            create_vendor(CreateVendorInput(context=ctx, name="Duplicate Vendor"))

    def test_duplicate_tax_id_fails(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        create_vendor(CreateVendorInput(context=ctx, name="Vendor 1", tax_id="SAME-TAX"))
        with pytest.raises(ProcurementError, match="tax ID 'SAME-TAX' already exists"):
            create_vendor(CreateVendorInput(context=ctx, name="Vendor 2", tax_id="SAME-TAX"))

    def test_update_vendor(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        v_res = create_vendor(CreateVendorInput(context=ctx, name="Old Name"))
        up_res = update_vendor(
            UpdateVendorInput(
                context=ctx,
                vendor_id=v_res.vendor_id,
                name="New Name",
                default_payment_terms="Net 60",
            )
        )
        assert up_res.name == "New Name"
        vendor = Vendor.objects.get(id=v_res.vendor_id)
        assert vendor.name == "New Name"
        assert vendor.default_payment_terms == "Net 60"

    def test_deactivate_vendor(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        v_res = create_vendor(CreateVendorInput(context=ctx, name="To Deactivate"))
        deact_res = deactivate_vendor(
            DeactivateVendorInput(
                context=ctx,
                vendor_id=v_res.vendor_id,
                reason="Vendor ceased operations",
            )
        )
        assert deact_res.is_active is False
        assert deact_res.deactivation_reason == "Vendor ceased operations"

        # Updating deactivated vendor fails
        with pytest.raises(InactiveVendorError):
            update_vendor(
                UpdateVendorInput(
                    context=ctx,
                    vendor_id=v_res.vendor_id,
                    name="Attempt Update",
                )
            )


@pytest.mark.django_db
class TestPurchaseRequisitionLifecycle:
    def test_create_and_update_draft_requisition(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        org_id, ctx = org_context
        req_res = create_purchase_requisition(
            CreatePurchaseRequisitionInput(
                context=ctx,
                title="Q1 School Materials",
                items=[
                    CreateRequisitionItemInput(
                        description="Exercise Books",
                        quantity=Decimal("500"),
                        unit="books",
                        estimated_unit_price=Decimal("2.50"),
                    ),
                    CreateRequisitionItemInput(
                        description="Blue Pens",
                        quantity=Decimal("300"),
                        unit="boxes",
                        estimated_unit_price=Decimal("1.20"),
                    ),
                ],
            )
        )
        assert req_res.authorization_status == AuthorizationStatus.DRAFT.value
        assert req_res.requisition_number.startswith("PR-")
        assert req_res.total_estimated_cost == Decimal("1610.00")  # 500*2.50 + 300*1.20 = 1250 + 360

        # Update draft requisition
        up_res = update_draft_requisition(
            UpdateDraftRequisitionInput(
                context=ctx,
                requisition_id=req_res.requisition_id,
                title="Q1 Revised School Materials",
                items=[
                    CreateRequisitionItemInput(
                        description="Exercise Books",
                        quantity=Decimal("600"),
                        unit="books",
                        estimated_unit_price=Decimal("2.50"),
                    ),
                ],
            )
        )
        assert up_res.title == "Q1 Revised School Materials"
        assert up_res.total_estimated_cost == Decimal("1500.00")

    def test_submit_empty_requisition_fails(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        req_res = create_purchase_requisition(
            CreatePurchaseRequisitionInput(
                context=ctx,
                title="Empty Requisition",
                items=[],
            )
        )
        with pytest.raises(EmptyRequisitionError):
            submit_purchase_requisition(
                SubmitPurchaseRequisitionInput(
                    context=ctx,
                    requisition_id=req_res.requisition_id,
                )
            )

    def test_approval_and_segregation_of_duties(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        req_res = create_purchase_requisition(
            CreatePurchaseRequisitionInput(
                context=ctx,
                title="Dormitory Food Supplies",
                items=[
                    CreateRequisitionItemInput(
                        description="Rice 50kg Bags",
                        quantity=Decimal("50"),
                        unit="bags",
                        estimated_unit_price=Decimal("40.00"),
                    )
                ],
            )
        )
        submit_purchase_requisition(
            SubmitPurchaseRequisitionInput(
                context=ctx,
                requisition_id=req_res.requisition_id,
            )
        )

        # Self-approval fails!
        with pytest.raises(SelfApprovalError):
            approve_purchase_requisition(
                ApprovePurchaseRequisitionInput(
                    context=ctx,
                    requisition_id=req_res.requisition_id,
                )
            )

        # Different approver succeeds
        approver_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=ctx.organization_id,
            correlation_id=uuid.uuid4(),
            actor_role="owner",
        )
        app_res = approve_purchase_requisition(
            ApprovePurchaseRequisitionInput(
                context=approver_ctx,
                requisition_id=req_res.requisition_id,
            )
        )
        assert app_res.authorization_status == AuthorizationStatus.APPROVED.value
        assert app_res.approved_by == approver_ctx.actor_id

        # Cannot edit approved requisition
        with pytest.raises(InvalidRequisitionTransitionError):
            update_draft_requisition(
                UpdateDraftRequisitionInput(
                    context=ctx,
                    requisition_id=req_res.requisition_id,
                    title="Attempt Edit",
                )
            )

    def test_rejection_and_return_to_draft(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        req_res = create_purchase_requisition(
            CreatePurchaseRequisitionInput(
                context=ctx,
                title="Office Luxury Chairs",
                items=[
                    CreateRequisitionItemInput(
                        description="Chairs",
                        quantity=Decimal("10"),
                        unit="pcs",
                        estimated_unit_price=Decimal("500.00"),
                    )
                ],
            )
        )
        submit_purchase_requisition(
            SubmitPurchaseRequisitionInput(
                context=ctx,
                requisition_id=req_res.requisition_id,
            )
        )

        approver_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=ctx.organization_id,
            correlation_id=uuid.uuid4(),
            actor_role="admin",
        )
        rej_res = reject_purchase_requisition(
            RejectPurchaseRequisitionInput(
                context=approver_ctx,
                requisition_id=req_res.requisition_id,
                rejection_reason="Exceeds budget cap for office furniture.",
            )
        )
        assert rej_res.authorization_status == AuthorizationStatus.REJECTED.value

        # Requester returns rejected requisition to draft for revision
        rev_res = return_requisition_to_draft(
            ReturnRequisitionToDraftInput(
                context=ctx,
                requisition_id=req_res.requisition_id,
            )
        )
        assert rev_res.authorization_status == AuthorizationStatus.DRAFT.value
        req = PurchaseRequisition.objects.get(id=req_res.requisition_id)
        assert req.rejection_reason == ""


@pytest.mark.django_db
class TestPurchaseOrderLifecycle:
    def test_po_creation_with_line_allocation(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        vendor_res = create_vendor(
            CreateVendorInput(
                context=ctx,
                name="Stationery Mega Store",
                default_payment_terms="Net 30",
            )
        )
        req_res = create_purchase_requisition(
            CreatePurchaseRequisitionInput(
                context=ctx,
                title="Books & Pens",
                items=[
                    CreateRequisitionItemInput(
                        description="Exercise Books",
                        quantity=Decimal("100"),
                        unit="books",
                        estimated_unit_price=Decimal("2.00"),
                    )
                ],
            )
        )
        submit_purchase_requisition(SubmitPurchaseRequisitionInput(context=ctx, requisition_id=req_res.requisition_id))
        approver_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=ctx.organization_id,
            correlation_id=uuid.uuid4(),
            actor_role="owner",
        )
        approve_purchase_requisition(
            ApprovePurchaseRequisitionInput(
                context=approver_ctx,
                requisition_id=req_res.requisition_id,
            )
        )

        req = PurchaseRequisition.objects.get(id=req_res.requisition_id)
        req_item = req.items.first()
        assert req_item is not None

        # Create PO fulfilling 60 of the 100 requested
        po_res = create_purchase_order(
            CreatePurchaseOrderInput(
                context=ctx,
                vendor_id=vendor_res.vendor_id,
                requisition_id=req_res.requisition_id,
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Exercise Books",
                        quantity=Decimal("60"),
                        unit="books",
                        unit_price=Decimal("1.90"),
                        allocations=[
                            CreateAllocationInput(
                                requisition_item_id=req_item.id,
                                allocated_quantity=Decimal("60"),
                            )
                        ],
                    )
                ],
            )
        )
        assert po_res.order_number.startswith("PO-")
        assert po_res.status == PurchaseOrderStatus.DRAFT.value
        assert po_res.total_amount == Decimal("114.00")  # 60 * 1.90

        # Try to over-allocate the remaining 40 with a 50 allocation
        with pytest.raises(OverAllocationError):
            create_purchase_order(
                CreatePurchaseOrderInput(
                    context=ctx,
                    vendor_id=vendor_res.vendor_id,
                    requisition_id=req_res.requisition_id,
                    items=[
                        CreatePurchaseOrderItemInput(
                            description="Exercise Books - Second Batch",
                            quantity=Decimal("50"),
                            unit="books",
                            unit_price=Decimal("1.90"),
                            allocations=[
                                CreateAllocationInput(
                                    requisition_item_id=req_item.id,
                                    allocated_quantity=Decimal("50"),
                                )
                            ],
                        )
                    ],
                )
            )

    def test_po_issuance_and_cancellation(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        v_res = create_vendor(
            CreateVendorInput(
                context=ctx,
                name="Hardware Store",
                default_payment_terms="Net 45",
            )
        )
        po_res = create_purchase_order(
            CreatePurchaseOrderInput(
                context=ctx,
                vendor_id=v_res.vendor_id,
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Hammer",
                        quantity=Decimal("5"),
                        unit="pcs",
                        unit_price=Decimal("15.00"),
                    )
                ],
            )
        )

        issue_res = issue_purchase_order(IssuePurchaseOrderInput(context=ctx, order_id=po_res.order_id))
        assert issue_res.status == PurchaseOrderStatus.ISSUED.value
        assert issue_res.payment_terms == "Net 45"

        cancel_res = cancel_purchase_order(
            CancelPurchaseOrderInput(
                context=ctx,
                order_id=po_res.order_id,
                cancellation_reason="Project cancelled by donor.",
            )
        )
        assert cancel_res.status == PurchaseOrderStatus.CANCELLED.value

    def test_close_purchase_order(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        v_res = create_vendor(CreateVendorInput(context=ctx, name="Printer Supplier"))
        po_res = create_purchase_order(
            CreatePurchaseOrderInput(
                context=ctx,
                vendor_id=v_res.vendor_id,
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Printer",
                        quantity=Decimal("1"),
                        unit="each",
                        unit_price=Decimal("350.00"),
                    )
                ],
            )
        )
        issue_purchase_order(IssuePurchaseOrderInput(context=ctx, order_id=po_res.order_id))
        close_res = close_purchase_order(ClosePurchaseOrderInput(context=ctx, order_id=po_res.order_id))
        assert close_res.status == PurchaseOrderStatus.CLOSED.value


@pytest.mark.django_db
class TestGoodsReceiptAndInspection:
    def test_grn_recording_and_inspection(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        v_res = create_vendor(CreateVendorInput(context=ctx, name="Grain Wholesaler"))
        po_res = create_purchase_order(
            CreatePurchaseOrderInput(
                context=ctx,
                vendor_id=v_res.vendor_id,
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Wheat Grain 100kg",
                        quantity=Decimal("20"),
                        unit="bags",
                        unit_price=Decimal("80.00"),
                    )
                ],
            )
        )
        issue_purchase_order(IssuePurchaseOrderInput(context=ctx, order_id=po_res.order_id))

        order = PurchaseOrder.objects.get(id=po_res.order_id)
        po_item = order.items.first()
        assert po_item is not None

        # Record GRN for 20 bags
        grn_res = record_goods_receipt(
            RecordGoodsReceiptInput(
                context=ctx,
                purchase_order_id=order.id,
                received_date=date.today(),
                receipt_type=ReceiptType.GOODS.value,
                items=[
                    RecordReceiptItemInput(
                        po_item_id=po_item.id,
                        quantity_received=Decimal("20"),
                    )
                ],
            )
        )
        assert grn_res.receipt_number.startswith("GRN-")
        assert grn_res.is_fully_inspected is False

        grn = GoodsReceiptNote.objects.get(id=grn_res.receipt_id)
        grn_item = grn.items.first()
        assert grn_item is not None

        # Inspection quantity mismatch fails (18 accepted + 1 rejected != 20 received)
        with pytest.raises(InspectionQuantityError):
            inspect_goods_receipt(
                InspectGoodsReceiptInput(
                    context=ctx,
                    receipt_id=grn.id,
                    inspections=[
                        InspectReceiptItemInput(
                            grn_item_id=grn_item.id,
                            quantity_accepted=Decimal("18"),
                            quantity_rejected=Decimal("1"),
                        )
                    ],
                )
            )

        # Proper inspection: 18 accepted, 2 rejected due to moisture damage
        insp_res = inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=ctx,
                receipt_id=grn.id,
                inspections=[
                    InspectReceiptItemInput(
                        grn_item_id=grn_item.id,
                        quantity_accepted=Decimal("18"),
                        quantity_rejected=Decimal("2"),
                        rejection_reason="Moisture damage during transport",
                    )
                ],
            )
        )
        assert insp_res.is_fully_inspected is True
        assert insp_res.has_rejections is True

        # Now attempting to cancel PO should be blocked because of accepted receipts!
        with pytest.raises(CancellationBlockedError):
            cancel_purchase_order(
                CancelPurchaseOrderInput(
                    context=ctx,
                    order_id=order.id,
                    cancellation_reason="Attempt cancel",
                )
            )

    def test_cannot_record_grn_against_draft_po(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        v_res = create_vendor(CreateVendorInput(context=ctx, name="Draft Vendor"))
        po_res = create_purchase_order(
            CreatePurchaseOrderInput(
                context=ctx,
                vendor_id=v_res.vendor_id,
                items=[
                    CreatePurchaseOrderItemInput(
                        description="Item 1",
                        quantity=Decimal("10"),
                        unit="pcs",
                        unit_price=Decimal("10.00"),
                    )
                ],
            )
        )
        order = PurchaseOrder.objects.get(id=po_res.order_id)
        po_item = order.items.first()
        assert po_item is not None

        with pytest.raises(ProcurementError, match="Order must be issued"):
            record_goods_receipt(
                RecordGoodsReceiptInput(
                    context=ctx,
                    purchase_order_id=order.id,
                    received_date=date.today(),
                    items=[
                        RecordReceiptItemInput(
                            po_item_id=po_item.id,
                            quantity_received=Decimal("10"),
                        )
                    ],
                )
            )


@pytest.mark.django_db
class TestCrossTenantIntegrity:
    """Rigorous tenant isolation checks (P0-5)."""

    def test_vendor_from_org_a_cannot_be_used_in_org_b(
        self,
        org_context: tuple[uuid.UUID, ExecutionContext],
    ):
        org_a_id, ctx_a = org_context
        v_res = create_vendor(CreateVendorInput(context=ctx_a, name="Org A Vendor"))

        # Create Org B
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org_b_res = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Org B",
                slug=f"org-b-{uuid.uuid4().hex[:6]}",
            )
        )
        ctx_b = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org_b_res.organization_id,
            correlation_id=uuid.uuid4(),
            actor_role="admin",
        )

        with pytest.raises(OrganizationMismatchError):
            create_purchase_order(
                CreatePurchaseOrderInput(
                    context=ctx_b,
                    vendor_id=v_res.vendor_id,
                    items=[
                        CreatePurchaseOrderItemInput(
                            description="Test Item",
                            quantity=Decimal("1"),
                            unit_price=Decimal("10.00"),
                        )
                    ],
                )
            )

    def test_requisition_from_org_a_cannot_be_linked_in_org_b(
        self,
        org_context: tuple[uuid.UUID, ExecutionContext],
    ):
        org_a_id, ctx_a = org_context
        req_res = create_purchase_requisition(
            CreatePurchaseRequisitionInput(
                context=ctx_a,
                title="Org A Requisition",
                items=[
                    CreateRequisitionItemInput(
                        description="Test",
                        quantity=Decimal("5"),
                        estimated_unit_price=Decimal("10.00"),
                    )
                ],
            )
        )

        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org_b_res = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Org B 2",
                slug=f"org-b-2-{uuid.uuid4().hex[:6]}",
            )
        )
        ctx_b = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org_b_res.organization_id,
            correlation_id=uuid.uuid4(),
            actor_role="admin",
        )
        v_b = create_vendor(CreateVendorInput(context=ctx_b, name="Org B Vendor"))

        with pytest.raises(OrganizationMismatchError):
            create_purchase_order(
                CreatePurchaseOrderInput(
                    context=ctx_b,
                    vendor_id=v_b.vendor_id,
                    requisition_id=req_res.requisition_id,
                    items=[
                        CreatePurchaseOrderItemInput(
                            description="Test",
                            quantity=Decimal("5"),
                            unit_price=Decimal("10.00"),
                        )
                    ],
                )
            )
