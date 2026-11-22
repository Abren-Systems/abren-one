import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

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
from abren_one.modules.procurement.application.commands.update_draft_purchase_order import (
    UpdateDraftPurchaseOrderInput,
)
from abren_one.modules.procurement.application.commands.update_draft_purchase_order import (
    execute as update_draft_purchase_order,
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
from abren_one.modules.procurement.application.queries.list_goods_receipts import (
    execute as list_goods_receipts,
)
from abren_one.modules.procurement.application.queries.list_purchase_orders import (
    execute as list_purchase_orders,
)
from abren_one.modules.procurement.application.queries.list_purchase_requisitions import (
    execute as list_purchase_requisitions,
)
from abren_one.modules.procurement.application.queries.list_vendors import (
    execute as list_vendors,
)
from abren_one.modules.procurement.interfaces.api.v1.serializers import (
    CancelPurchaseOrderRequestSerializer,
    CreatePurchaseOrderRequestSerializer,
    CreateRequisitionRequestSerializer,
    CreateVendorRequestSerializer,
    DeactivateVendorRequestSerializer,
    GoodsReceiptDetailResponseSerializer,
    GoodsReceiptSummaryResponseSerializer,
    InspectGoodsReceiptRequestSerializer,
    OrderDeliveryPositionResponseSerializer,
    PurchaseOrderDetailResponseSerializer,
    PurchaseOrderSummaryResponseSerializer,
    RecordGoodsReceiptRequestSerializer,
    RejectRequisitionRequestSerializer,
    RequisitionDetailResponseSerializer,
    RequisitionFulfillmentResponseSerializer,
    RequisitionSummaryResponseSerializer,
    UpdateDraftPurchaseOrderRequestSerializer,
    UpdateDraftRequisitionRequestSerializer,
    UpdateVendorRequestSerializer,
    VendorDetailResponseSerializer,
    VendorSummaryResponseSerializer,
)
from abren_one.platform.authorization.permissions import require_permission
from abren_one.platform.common.context import build_execution_context
from abren_one.platform.tenancy.permissions import HasOrganizationContext

# ── Vendor Views ──────────────────────────────────────────────────────────────


class VendorListCreateView(APIView):
    """List and create vendors."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("procurement:vendors:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("procurement:vendors:view")(),
        ]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        vendor_type = request.query_params.get("vendor_type")
        is_active_param = request.query_params.get("is_active")
        is_active = None
        if is_active_param is not None:
            is_active = is_active_param.lower() in ("true", "1")
        verification_status = request.query_params.get("verification_status")

        try:
            limit = max(1, min(int(request.query_params.get("limit", 100)), 500))
        except ValueError, TypeError:
            limit = 100
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        vendors = list_vendors(
            context=ctx,
            vendor_type=vendor_type,
            is_active=is_active,
            verification_status=verification_status,
            limit=limit,
            offset=offset,
        )
        serializer = VendorSummaryResponseSerializer(vendors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = CreateVendorRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        result = create_vendor(
            CreateVendorInput(
                context=ctx,
                name=validated["name"],
                vendor_type=validated.get("vendor_type", "goods"),
                tax_id=validated.get("tax_id", ""),
                country=validated.get("country", ""),
                contact_name=validated.get("contact_name", ""),
                email=validated.get("email", ""),
                phone=validated.get("phone", ""),
                address=validated.get("address", ""),
                default_payment_terms=validated.get("default_payment_terms", ""),
                default_currency=validated.get("default_currency", "USD"),
                notes=validated.get("notes", ""),
            )
        )
        return Response(
            {
                "vendor_id": result.vendor_id,
                "name": result.name,
                "vendor_type": result.vendor_type,
                "is_active": result.is_active,
                "verification_status": result.verification_status,
            },
            status=status.HTTP_201_CREATED,
        )


class VendorDetailUpdateView(APIView):
    """Retrieve and update an individual vendor."""

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("procurement:vendors:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("procurement:vendors:view")(),
        ]

    def get(self, request: Request, vendor_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        vendor = get_vendor(ctx, vendor_id)
        serializer = VendorDetailResponseSerializer(vendor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, vendor_id: uuid.UUID) -> Response:
        serializer = UpdateVendorRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        result = update_vendor(
            UpdateVendorInput(
                context=ctx,
                vendor_id=vendor_id,
                name=validated.get("name"),
                vendor_type=validated.get("vendor_type"),
                tax_id=validated.get("tax_id"),
                country=validated.get("country"),
                contact_name=validated.get("contact_name"),
                email=validated.get("email"),
                phone=validated.get("phone"),
                address=validated.get("address"),
                default_payment_terms=validated.get("default_payment_terms"),
                default_currency=validated.get("default_currency"),
                verification_status=validated.get("verification_status"),
                notes=validated.get("notes"),
            )
        )
        return Response(
            {
                "vendor_id": result.vendor_id,
                "name": result.name,
                "vendor_type": result.vendor_type,
                "is_active": result.is_active,
                "verification_status": result.verification_status,
            },
            status=status.HTTP_200_OK,
        )


class DeactivateVendorView(APIView):
    """Deactivate a vendor with mandatory reason."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("procurement:vendors:manage"),
    ]

    def post(self, request: Request, vendor_id: uuid.UUID) -> Response:
        serializer = DeactivateVendorRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ctx = build_execution_context(request)
        result = deactivate_vendor(
            DeactivateVendorInput(
                context=ctx,
                vendor_id=vendor_id,
                reason=serializer.validated_data["reason"],
            )
        )
        return Response(
            {
                "vendor_id": result.vendor_id,
                "is_active": result.is_active,
                "deactivation_reason": result.deactivation_reason,
            },
            status=status.HTTP_200_OK,
        )


# ── Purchase Requisition Views ────────────────────────────────────────────────


class RequisitionListCreateView(APIView):
    """List and create purchase requisitions."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("procurement:requisitions:create")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("procurement:requisitions:view")(),
        ]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        auth_status = request.query_params.get("authorization_status")
        req_by_param = request.query_params.get("requested_by")
        requested_by = uuid.UUID(req_by_param) if req_by_param else None

        try:
            limit = max(1, min(int(request.query_params.get("limit", 100)), 500))
        except ValueError, TypeError:
            limit = 100
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        reqs = list_purchase_requisitions(
            context=ctx,
            authorization_status=auth_status,
            requested_by=requested_by,
            limit=limit,
            offset=offset,
        )
        serializer = RequisitionSummaryResponseSerializer(reqs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = CreateRequisitionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        item_inputs = [
            CreateRequisitionItemInput(
                description=it["description"],
                quantity=it["quantity"],
                unit=it.get("unit", "each"),
                estimated_unit_price=it.get("estimated_unit_price", 0),
                program_id=it.get("program_id"),
                activity_id=it.get("activity_id"),
                department_id=it.get("department_id"),
            )
            for it in validated.get("items", [])
        ]

        result = create_purchase_requisition(
            CreatePurchaseRequisitionInput(
                context=ctx,
                title=validated["title"],
                items=item_inputs,
                currency=validated.get("currency", "USD"),
                notes=validated.get("notes", ""),
            )
        )
        return Response(
            {
                "requisition_id": result.requisition_id,
                "requisition_number": result.requisition_number,
                "title": result.title,
                "authorization_status": result.authorization_status,
                "total_estimated_cost": str(result.total_estimated_cost),
            },
            status=status.HTTP_201_CREATED,
        )


class RequisitionDetailUpdateView(APIView):
    """Retrieve full detail of a requisition or update it while in DRAFT status."""

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("procurement:requisitions:create")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("procurement:requisitions:view")(),
        ]

    def get(self, request: Request, requisition_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        req = get_purchase_requisition(ctx, requisition_id)
        serializer = RequisitionDetailResponseSerializer(req)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, requisition_id: uuid.UUID) -> Response:
        serializer = UpdateDraftRequisitionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        item_inputs = None
        items_raw = validated.get("items")
        if items_raw is not None:
            item_inputs = [
                CreateRequisitionItemInput(
                    description=it["description"],
                    quantity=it["quantity"],
                    unit=it.get("unit", "each"),
                    estimated_unit_price=it.get("estimated_unit_price", 0),
                    program_id=it.get("program_id"),
                    activity_id=it.get("activity_id"),
                    department_id=it.get("department_id"),
                )
                for it in items_raw
            ]

        result = update_draft_requisition(
            UpdateDraftRequisitionInput(
                context=ctx,
                requisition_id=requisition_id,
                title=validated.get("title"),
                currency=validated.get("currency"),
                notes=validated.get("notes"),
                items=item_inputs,
            )
        )
        return Response(
            {
                "requisition_id": result.requisition_id,
                "requisition_number": result.requisition_number,
                "title": result.title,
                "authorization_status": result.authorization_status,
                "total_estimated_cost": str(result.total_estimated_cost),
            },
            status=status.HTTP_200_OK,
        )


class SubmitRequisitionView(APIView):
    """Submit a draft requisition for authorization."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("procurement:requisitions:create"),
    ]

    def post(self, request: Request, requisition_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        result = submit_purchase_requisition(
            SubmitPurchaseRequisitionInput(
                context=ctx,
                requisition_id=requisition_id,
            )
        )
        return Response(
            {
                "requisition_id": result.requisition_id,
                "requisition_number": result.requisition_number,
                "authorization_status": result.authorization_status,
            },
            status=status.HTTP_200_OK,
        )


class ApproveRequisitionView(APIView):
    """Approve a submitted requisition (segregation of duties enforced)."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("procurement:requisitions:approve"),
    ]

    def post(self, request: Request, requisition_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        result = approve_purchase_requisition(
            ApprovePurchaseRequisitionInput(
                context=ctx,
                requisition_id=requisition_id,
            )
        )
        return Response(
            {
                "requisition_id": result.requisition_id,
                "requisition_number": result.requisition_number,
                "authorization_status": result.authorization_status,
                "approved_by": result.approved_by,
                "approved_at": result.approved_at,
            },
            status=status.HTTP_200_OK,
        )


class RejectRequisitionView(APIView):
    """Reject a submitted requisition with reason."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("procurement:requisitions:approve"),
    ]

    def post(self, request: Request, requisition_id: uuid.UUID) -> Response:
        serializer = RejectRequisitionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ctx = build_execution_context(request)
        result = reject_purchase_requisition(
            RejectPurchaseRequisitionInput(
                context=ctx,
                requisition_id=requisition_id,
                rejection_reason=serializer.validated_data["rejection_reason"],
            )
        )
        return Response(
            {
                "requisition_id": result.requisition_id,
                "requisition_number": result.requisition_number,
                "authorization_status": result.authorization_status,
                "rejection_reason": result.rejection_reason,
            },
            status=status.HTTP_200_OK,
        )


class ReturnRequisitionView(APIView):
    """Return a submitted or rejected requisition to draft for revision."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("procurement:requisitions:create"),
    ]

    def post(self, request: Request, requisition_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        result = return_requisition_to_draft(
            ReturnRequisitionToDraftInput(
                context=ctx,
                requisition_id=requisition_id,
            )
        )
        return Response(
            {
                "requisition_id": result.requisition_id,
                "requisition_number": result.requisition_number,
                "authorization_status": result.authorization_status,
            },
            status=status.HTTP_200_OK,
        )


class RequisitionFulfillmentView(APIView):
    """Retrieve derived fulfillment position across all order line allocations and receipts."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("procurement:requisitions:view"),
    ]

    def get(self, request: Request, requisition_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        result = get_requisition_fulfillment(ctx, requisition_id)
        serializer = RequisitionFulfillmentResponseSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ── Purchase Order Views ──────────────────────────────────────────────────────


class PurchaseOrderListCreateView(APIView):
    """List and create purchase orders."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("procurement:orders:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("procurement:orders:view")(),
        ]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        po_status = request.query_params.get("status")
        vendor_id_param = request.query_params.get("vendor_id")
        vendor_id = uuid.UUID(vendor_id_param) if vendor_id_param else None

        try:
            limit = max(1, min(int(request.query_params.get("limit", 100)), 500))
        except ValueError, TypeError:
            limit = 100
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        orders = list_purchase_orders(
            context=ctx,
            status=po_status,
            vendor_id=vendor_id,
            limit=limit,
            offset=offset,
        )
        serializer = PurchaseOrderSummaryResponseSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = CreatePurchaseOrderRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        item_inputs = []
        for it in validated.get("items", []):
            allocs = [
                CreateAllocationInput(
                    requisition_item_id=al["requisition_item_id"],
                    allocated_quantity=al["allocated_quantity"],
                )
                for al in it.get("allocations", [])
            ]
            item_inputs.append(
                CreatePurchaseOrderItemInput(
                    description=it["description"],
                    quantity=it["quantity"],
                    unit=it.get("unit", "each"),
                    unit_price=it.get("unit_price", 0),
                    allocations=allocs,
                )
            )

        result = create_purchase_order(
            CreatePurchaseOrderInput(
                context=ctx,
                vendor_id=validated["vendor_id"],
                requisition_id=validated.get("requisition_id"),
                currency=validated.get("currency", "USD"),
                expected_delivery_date=validated.get("expected_delivery_date"),
                delivery_address=validated.get("delivery_address", ""),
                terms_and_conditions=validated.get("terms_and_conditions", ""),
                notes=validated.get("notes", ""),
                items=item_inputs,
            )
        )
        return Response(
            {
                "order_id": result.order_id,
                "order_number": result.order_number,
                "vendor_id": result.vendor_id,
                "status": result.status,
                "total_amount": str(result.total_amount),
            },
            status=status.HTTP_201_CREATED,
        )


class PurchaseOrderDetailUpdateView(APIView):
    """Retrieve full detail of a purchase order or update draft details."""

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("procurement:orders:manage")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("procurement:orders:view")(),
        ]

    def get(self, request: Request, order_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        order = get_purchase_order(ctx, order_id)
        serializer = PurchaseOrderDetailResponseSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, order_id: uuid.UUID) -> Response:
        serializer = UpdateDraftPurchaseOrderRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        item_inputs = None
        items_raw = validated.get("items")
        if items_raw is not None:
            item_inputs = []
            for it in items_raw:
                allocs = [
                    CreateAllocationInput(
                        requisition_item_id=al["requisition_item_id"],
                        allocated_quantity=al["allocated_quantity"],
                    )
                    for al in it.get("allocations", [])
                ]
                item_inputs.append(
                    CreatePurchaseOrderItemInput(
                        description=it["description"],
                        quantity=it["quantity"],
                        unit=it.get("unit", "each"),
                        unit_price=it.get("unit_price", 0),
                        allocations=allocs,
                    )
                )

        result = update_draft_purchase_order(
            UpdateDraftPurchaseOrderInput(
                context=ctx,
                order_id=order_id,
                vendor_id=validated.get("vendor_id"),
                currency=validated.get("currency"),
                expected_delivery_date=validated.get("expected_delivery_date"),
                delivery_address=validated.get("delivery_address"),
                terms_and_conditions=validated.get("terms_and_conditions"),
                notes=validated.get("notes"),
                items=item_inputs,
            )
        )
        return Response(
            {
                "order_id": result.order_id,
                "order_number": result.order_number,
                "status": result.status,
                "total_amount": str(result.total_amount),
            },
            status=status.HTTP_200_OK,
        )


class IssuePurchaseOrderView(APIView):
    """Issue a purchase order to vendor."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("procurement:orders:manage"),
    ]

    def post(self, request: Request, order_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        result = issue_purchase_order(
            IssuePurchaseOrderInput(
                context=ctx,
                order_id=order_id,
            )
        )
        return Response(
            {
                "order_id": result.order_id,
                "order_number": result.order_number,
                "status": result.status,
                "issued_at": result.issued_at,
                "payment_terms": result.payment_terms,
            },
            status=status.HTTP_200_OK,
        )


class CancelPurchaseOrderView(APIView):
    """Cancel a purchase order."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("procurement:orders:manage"),
    ]

    def post(self, request: Request, order_id: uuid.UUID) -> Response:
        serializer = CancelPurchaseOrderRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ctx = build_execution_context(request)
        result = cancel_purchase_order(
            CancelPurchaseOrderInput(
                context=ctx,
                order_id=order_id,
                cancellation_reason=serializer.validated_data["cancellation_reason"],
            )
        )
        return Response(
            {
                "order_id": result.order_id,
                "order_number": result.order_number,
                "status": result.status,
                "cancellation_reason": result.cancellation_reason,
                "cancelled_by": result.cancelled_by,
                "cancelled_at": result.cancelled_at,
            },
            status=status.HTTP_200_OK,
        )


class ClosePurchaseOrderView(APIView):
    """Explicitly close an issued purchase order."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("procurement:orders:manage"),
    ]

    def post(self, request: Request, order_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        result = close_purchase_order(
            ClosePurchaseOrderInput(
                context=ctx,
                order_id=order_id,
            )
        )
        return Response(
            {
                "order_id": result.order_id,
                "order_number": result.order_number,
                "status": result.status,
            },
            status=status.HTTP_200_OK,
        )


class OrderDeliveryPositionView(APIView):
    """Retrieve derived delivery position for an order across its goods receipts."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("procurement:orders:view"),
    ]

    def get(self, request: Request, order_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        result = get_order_delivery_position(ctx, order_id)
        serializer = OrderDeliveryPositionResponseSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ── Goods Receipt Views ───────────────────────────────────────────────────────


class GoodsReceiptListCreateView(APIView):
    """List and record goods receipts."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                HasOrganizationContext(),
                require_permission("procurement:receipts:record")(),
            ]
        return [
            IsAuthenticated(),
            HasOrganizationContext(),
            require_permission("procurement:receipts:view")(),
        ]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        po_id_param = request.query_params.get("purchase_order_id")
        po_id = uuid.UUID(po_id_param) if po_id_param else None

        try:
            limit = max(1, min(int(request.query_params.get("limit", 100)), 500))
        except ValueError, TypeError:
            limit = 100
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError, TypeError:
            offset = 0

        grns = list_goods_receipts(
            context=ctx,
            purchase_order_id=po_id,
            limit=limit,
            offset=offset,
        )
        serializer = GoodsReceiptSummaryResponseSerializer(grns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = RecordGoodsReceiptRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        item_inputs = [
            RecordReceiptItemInput(
                po_item_id=it["po_item_id"],
                quantity_received=it["quantity_received"],
            )
            for it in validated.get("items", [])
        ]

        result = record_goods_receipt(
            RecordGoodsReceiptInput(
                context=ctx,
                purchase_order_id=validated["purchase_order_id"],
                received_date=validated["received_date"],
                receipt_type=validated.get("receipt_type", "goods"),
                inspection_notes=validated.get("inspection_notes", ""),
                is_correction=validated.get("is_correction", False),
                corrects_id=validated.get("corrects_id"),
                items=item_inputs,
            )
        )
        return Response(
            {
                "receipt_id": result.receipt_id,
                "receipt_number": result.receipt_number,
                "purchase_order_id": result.purchase_order_id,
                "receipt_type": result.receipt_type,
                "is_fully_inspected": result.is_fully_inspected,
            },
            status=status.HTTP_201_CREATED,
        )


class GoodsReceiptDetailView(APIView):
    """Retrieve full detail of a goods receipt."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("procurement:receipts:view"),
    ]

    def get(self, request: Request, receipt_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        grn = get_goods_receipt(ctx, receipt_id)
        serializer = GoodsReceiptDetailResponseSerializer(grn)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InspectGoodsReceiptView(APIView):
    """Record inspection outcomes for items on a goods receipt note."""

    permission_classes = [
        IsAuthenticated,
        HasOrganizationContext,
        require_permission("procurement:receipts:inspect"),
    ]

    def post(self, request: Request, receipt_id: uuid.UUID) -> Response:
        serializer = InspectGoodsReceiptRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        inspection_inputs = [
            InspectReceiptItemInput(
                grn_item_id=it["grn_item_id"],
                quantity_accepted=it["quantity_accepted"],
                quantity_rejected=it["quantity_rejected"],
                rejection_reason=it.get("rejection_reason", ""),
            )
            for it in validated["inspections"]
        ]

        result = inspect_goods_receipt(
            InspectGoodsReceiptInput(
                context=ctx,
                receipt_id=receipt_id,
                inspections=inspection_inputs,
            )
        )
        return Response(
            {
                "receipt_id": result.receipt_id,
                "receipt_number": result.receipt_number,
                "is_fully_inspected": result.is_fully_inspected,
                "has_rejections": result.has_rejections,
            },
            status=status.HTTP_200_OK,
        )
