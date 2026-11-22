from decimal import Decimal

from rest_framework import serializers

# ── Vendor Serializers ────────────────────────────────────────────────────────


class CreateVendorRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    vendor_type = serializers.ChoiceField(
        choices=["goods", "services", "consulting"],
        default="goods",
    )
    tax_id = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    country = serializers.CharField(max_length=3, required=False, allow_blank=True, default="")
    contact_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    phone = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    address = serializers.CharField(required=False, allow_blank=True, default="")
    default_payment_terms = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    default_currency = serializers.CharField(max_length=3, default="USD")
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class UpdateVendorRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    vendor_type = serializers.ChoiceField(
        choices=["goods", "services", "consulting"],
        required=False,
    )
    tax_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    country = serializers.CharField(max_length=3, required=False, allow_blank=True)
    contact_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    default_payment_terms = serializers.CharField(max_length=100, required=False, allow_blank=True)
    default_currency = serializers.CharField(max_length=3, required=False)
    verification_status = serializers.ChoiceField(
        choices=["unverified", "verified", "suspended"],
        required=False,
    )
    notes = serializers.CharField(required=False, allow_blank=True)


class DeactivateVendorRequestSerializer(serializers.Serializer):
    reason = serializers.CharField()


class VendorSummaryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    vendor_type = serializers.CharField()
    tax_id = serializers.CharField()
    country = serializers.CharField()
    contact_name = serializers.CharField()
    email = serializers.CharField()
    is_active = serializers.BooleanField()
    verification_status = serializers.CharField()
    default_currency = serializers.CharField()


class VendorDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    vendor_type = serializers.CharField()
    tax_id = serializers.CharField()
    country = serializers.CharField()
    contact_name = serializers.CharField()
    email = serializers.CharField()
    phone = serializers.CharField()
    address = serializers.CharField()
    default_payment_terms = serializers.CharField()
    default_currency = serializers.CharField()
    verification_status = serializers.CharField()
    is_active = serializers.BooleanField()
    deactivation_reason = serializers.CharField()
    notes = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


# ── Purchase Requisition Serializers ──────────────────────────────────────────


class CreateRequisitionItemSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=500)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit = serializers.CharField(max_length=50, default="each")
    estimated_unit_price = serializers.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    program_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    activity_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    department_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class CreateRequisitionRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    items = CreateRequisitionItemSerializer(many=True, required=False, default=list)
    currency = serializers.CharField(max_length=3, default="USD")
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class UpdateDraftRequisitionRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    currency = serializers.CharField(max_length=3, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    items = CreateRequisitionItemSerializer(many=True, required=False)


class RejectRequisitionRequestSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField()


class RequisitionItemDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    description = serializers.CharField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit = serializers.CharField()
    estimated_unit_price = serializers.DecimalField(max_digits=15, decimal_places=2)
    line_total = serializers.DecimalField(max_digits=15, decimal_places=2)
    program_id = serializers.UUIDField(allow_null=True)
    activity_id = serializers.UUIDField(allow_null=True)
    department_id = serializers.UUIDField(allow_null=True)
    allocated_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    outstanding_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)


class RequisitionSummaryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    requisition_number = serializers.CharField()
    title = serializers.CharField()
    authorization_status = serializers.CharField()
    currency = serializers.CharField()
    total_estimated_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    requested_by = serializers.UUIDField()
    approved_by = serializers.UUIDField(allow_null=True)
    approved_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    item_count = serializers.IntegerField()


class RequisitionDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    requisition_number = serializers.CharField()
    title = serializers.CharField()
    authorization_status = serializers.CharField()
    currency = serializers.CharField()
    total_estimated_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    requested_by = serializers.UUIDField()
    approved_by = serializers.UUIDField(allow_null=True)
    approved_at = serializers.DateTimeField(allow_null=True)
    rejection_reason = serializers.CharField()
    notes = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    items = RequisitionItemDetailSerializer(many=True)


class RequisitionFulfillmentItemSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    description = serializers.CharField()
    quantity_requested = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit = serializers.CharField()
    quantity_ordered = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_accepted = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_outstanding_order = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_outstanding_delivery = serializers.DecimalField(max_digits=12, decimal_places=2)


class RequisitionFulfillmentResponseSerializer(serializers.Serializer):
    requisition_id = serializers.UUIDField()
    requisition_number = serializers.CharField()
    authorization_status = serializers.CharField()
    fulfillment_position = serializers.CharField()
    items = RequisitionFulfillmentItemSerializer(many=True)


# ── Purchase Order Serializers ────────────────────────────────────────────────


class CreateAllocationSerializer(serializers.Serializer):
    requisition_item_id = serializers.UUIDField()
    allocated_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)


class CreatePurchaseOrderItemSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=500)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit = serializers.CharField(max_length=50, default="each")
    unit_price = serializers.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    allocations = CreateAllocationSerializer(many=True, required=False, default=list)


class CreatePurchaseOrderRequestSerializer(serializers.Serializer):
    vendor_id = serializers.UUIDField()
    requisition_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    currency = serializers.CharField(max_length=3, default="USD")
    expected_delivery_date = serializers.DateField(required=False, allow_null=True, default=None)
    delivery_address = serializers.CharField(required=False, allow_blank=True, default="")
    terms_and_conditions = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    items = CreatePurchaseOrderItemSerializer(many=True, required=False, default=list)


class UpdateDraftPurchaseOrderRequestSerializer(serializers.Serializer):
    vendor_id = serializers.UUIDField(required=False)
    currency = serializers.CharField(max_length=3, required=False)
    expected_delivery_date = serializers.DateField(required=False, allow_null=True)
    delivery_address = serializers.CharField(required=False, allow_blank=True)
    terms_and_conditions = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    items = CreatePurchaseOrderItemSerializer(many=True, required=False)


class CancelPurchaseOrderRequestSerializer(serializers.Serializer):
    cancellation_reason = serializers.CharField()


class PurchaseOrderItemDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    description = serializers.CharField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit = serializers.CharField()
    unit_price = serializers.DecimalField(max_digits=15, decimal_places=2)
    line_total = serializers.DecimalField(max_digits=15, decimal_places=2)
    quantity_received = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_accepted = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_outstanding = serializers.DecimalField(max_digits=12, decimal_places=2)


class PurchaseOrderSummaryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    order_number = serializers.CharField()
    vendor_id = serializers.UUIDField()
    vendor_name = serializers.CharField()
    requisition_id = serializers.UUIDField(allow_null=True)
    requisition_number = serializers.CharField()
    status = serializers.CharField()
    currency = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    payment_terms = serializers.CharField()
    issued_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    item_count = serializers.IntegerField()


class PurchaseOrderDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    order_number = serializers.CharField()
    vendor_id = serializers.UUIDField()
    vendor_name = serializers.CharField()
    requisition_id = serializers.UUIDField(allow_null=True)
    requisition_number = serializers.CharField()
    status = serializers.CharField()
    currency = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    payment_terms = serializers.CharField()
    issued_at = serializers.DateTimeField(allow_null=True)
    issued_by = serializers.UUIDField(allow_null=True)
    expected_delivery_date = serializers.DateField(allow_null=True)
    delivery_address = serializers.CharField()
    terms_and_conditions = serializers.CharField()
    cancellation_reason = serializers.CharField()
    cancelled_by = serializers.UUIDField(allow_null=True)
    cancelled_at = serializers.DateTimeField(allow_null=True)
    notes = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    items = PurchaseOrderItemDetailSerializer(many=True)


class OrderDeliveryItemSerializer(serializers.Serializer):
    po_item_id = serializers.UUIDField()
    description = serializers.CharField()
    quantity_ordered = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit = serializers.CharField()
    unit_price = serializers.DecimalField(max_digits=15, decimal_places=2)
    quantity_received = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_accepted = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_rejected = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_outstanding = serializers.DecimalField(max_digits=12, decimal_places=2)


class OrderDeliveryPositionResponseSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    order_number = serializers.CharField()
    status = serializers.CharField()
    delivery_position = serializers.CharField()
    items = OrderDeliveryItemSerializer(many=True)


# ── Goods Receipt Serializers ─────────────────────────────────────────────────


class RecordReceiptItemSerializer(serializers.Serializer):
    po_item_id = serializers.UUIDField()
    quantity_received = serializers.DecimalField(max_digits=12, decimal_places=2)


class RecordGoodsReceiptRequestSerializer(serializers.Serializer):
    purchase_order_id = serializers.UUIDField()
    received_date = serializers.DateField()
    receipt_type = serializers.ChoiceField(choices=["goods", "services"], default="goods")
    inspection_notes = serializers.CharField(required=False, allow_blank=True, default="")
    is_correction = serializers.BooleanField(default=False)
    corrects_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    items = RecordReceiptItemSerializer(many=True, required=False, default=list)


class InspectReceiptItemSerializer(serializers.Serializer):
    grn_item_id = serializers.UUIDField()
    quantity_accepted = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_rejected = serializers.DecimalField(max_digits=12, decimal_places=2)
    rejection_reason = serializers.CharField(required=False, allow_blank=True, default="")


class InspectGoodsReceiptRequestSerializer(serializers.Serializer):
    inspections = InspectReceiptItemSerializer(many=True)


class GoodsReceiptItemDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    po_item_id = serializers.UUIDField()
    description = serializers.CharField()
    quantity_received = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_accepted = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_rejected = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_inspected = serializers.BooleanField()
    rejection_reason = serializers.CharField()


class GoodsReceiptSummaryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    receipt_number = serializers.CharField()
    purchase_order_id = serializers.UUIDField()
    order_number = serializers.CharField()
    receipt_type = serializers.CharField()
    received_date = serializers.DateField()
    received_by = serializers.UUIDField()
    is_correction = serializers.BooleanField()
    is_fully_inspected = serializers.BooleanField()
    has_rejections = serializers.BooleanField()
    item_count = serializers.IntegerField()


class GoodsReceiptDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    receipt_number = serializers.CharField()
    purchase_order_id = serializers.UUIDField()
    order_number = serializers.CharField()
    receipt_type = serializers.CharField()
    received_date = serializers.DateField()
    received_by = serializers.UUIDField()
    inspection_notes = serializers.CharField()
    is_correction = serializers.BooleanField()
    corrects_id = serializers.UUIDField(allow_null=True)
    is_fully_inspected = serializers.BooleanField()
    has_rejections = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    items = GoodsReceiptItemDetailSerializer(many=True)
