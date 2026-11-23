from rest_framework import serializers

ITEM_TYPE_CHOICES = [
    "consumable",
    "durable_asset",
    "medical",
    "relief_aid",
    "office_supplies",
    "other",
]

WAREHOUSE_TYPE_CHOICES = [
    "central_warehouse",
    "regional_depot",
    "field_post",
    "transit_hub",
    "quarantine",
]


class CreateItemCategoryRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    code = serializers.CharField(max_length=50)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    parent_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class ItemCategoryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    code = serializers.CharField()
    description = serializers.CharField()
    parent_id = serializers.UUIDField(allow_null=True)
    parent_name = serializers.CharField(allow_null=True)


class CreateItemRequestSerializer(serializers.Serializer):
    category_id = serializers.UUIDField()
    item_code = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    unit_of_measure = serializers.CharField(max_length=50, default="each")
    item_type = serializers.ChoiceField(
        choices=ITEM_TYPE_CHOICES,
        default="consumable",
    )
    track_batches = serializers.BooleanField(default=False)
    track_expiry = serializers.BooleanField(default=False)
    reorder_threshold = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    default_unit_cost = serializers.DecimalField(max_digits=15, decimal_places=2, default=0)


class UpdateItemRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    category_id = serializers.UUIDField(required=False)
    unit_of_measure = serializers.CharField(max_length=50, required=False)
    item_type = serializers.ChoiceField(choices=ITEM_TYPE_CHOICES, required=False)
    track_batches = serializers.BooleanField(required=False)
    track_expiry = serializers.BooleanField(required=False)
    reorder_threshold = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    default_unit_cost = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    is_active = serializers.BooleanField(required=False)


class ItemSummaryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    item_code = serializers.CharField()
    name = serializers.CharField()
    category_id = serializers.UUIDField()
    category_name = serializers.CharField()
    unit_of_measure = serializers.CharField()
    item_type = serializers.CharField()
    track_batches = serializers.BooleanField()
    track_expiry = serializers.BooleanField()
    reorder_threshold = serializers.DecimalField(max_digits=12, decimal_places=2)
    default_unit_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    is_active = serializers.BooleanField()


class BatchSummaryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    batch_number = serializers.CharField()
    manufacture_date = serializers.DateField(allow_null=True)
    expiry_date = serializers.DateField(allow_null=True)


class ItemDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    item_code = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    category_id = serializers.UUIDField()
    category_name = serializers.CharField()
    category_code = serializers.CharField()
    unit_of_measure = serializers.CharField()
    item_type = serializers.CharField()
    track_batches = serializers.BooleanField()
    track_expiry = serializers.BooleanField()
    reorder_threshold = serializers.DecimalField(max_digits=12, decimal_places=2)
    default_unit_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    is_active = serializers.BooleanField()
    batches = BatchSummaryResponseSerializer(many=True)


class CreateItemBatchRequestSerializer(serializers.Serializer):
    batch_number = serializers.CharField(max_length=100)
    manufacture_date = serializers.DateField(required=False, allow_null=True, default=None)
    expiry_date = serializers.DateField(required=False, allow_null=True, default=None)


class CreateWarehouseRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=50)
    warehouse_type = serializers.ChoiceField(
        choices=WAREHOUSE_TYPE_CHOICES,
        default="regional_depot",
    )
    branch_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    custodian_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    address = serializers.CharField(required=False, allow_blank=True, default="")


class UpdateWarehouseRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    warehouse_type = serializers.ChoiceField(choices=WAREHOUSE_TYPE_CHOICES, required=False)
    branch_id = serializers.UUIDField(required=False, allow_null=True)
    custodian_id = serializers.UUIDField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)


class WarehouseSummaryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    code = serializers.CharField()
    warehouse_type = serializers.CharField()
    branch_id = serializers.UUIDField(allow_null=True)
    custodian_id = serializers.UUIDField(allow_null=True)
    is_active = serializers.BooleanField()
    location_count = serializers.IntegerField()


class LocationResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    code = serializers.CharField()
    is_active = serializers.BooleanField()


class WarehouseDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    code = serializers.CharField()
    warehouse_type = serializers.CharField()
    branch_id = serializers.UUIDField(allow_null=True)
    custodian_id = serializers.UUIDField(allow_null=True)
    address = serializers.CharField()
    is_active = serializers.BooleanField()
    locations = LocationResponseSerializer(many=True)


class CreateStorageLocationRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    code = serializers.CharField(max_length=50)


# ── Stock Movement Request Serializers ────────────────────────────────────────


class ReceiveOpeningStockLineSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = serializers.DecimalField(max_digits=15, decimal_places=2, default=0)
    location_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    batch_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class ReceiveOpeningStockRequestSerializer(serializers.Serializer):
    warehouse_id = serializers.UUIDField()
    transaction_date = serializers.DateField()
    reference_document = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    lines = ReceiveOpeningStockLineSerializer(many=True)


class ReceiveDonationLineSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = serializers.DecimalField(max_digits=15, decimal_places=2, default=0)
    location_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    batch_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class ReceiveDonationRequestSerializer(serializers.Serializer):
    warehouse_id = serializers.UUIDField()
    donor_name = serializers.CharField(max_length=255)
    transaction_date = serializers.DateField()
    reference_document = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    lines = ReceiveDonationLineSerializer(many=True)


class TransferLineSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    source_location_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    destination_location_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    batch_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class TransferStockRequestSerializer(serializers.Serializer):
    source_warehouse_id = serializers.UUIDField()
    destination_warehouse_id = serializers.UUIDField()
    transaction_date = serializers.DateField()
    reference_document = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    lines = TransferLineSerializer(many=True)


class IssueLineSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    location_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    batch_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    program_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    activity_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class IssueStockRequestSerializer(serializers.Serializer):
    warehouse_id = serializers.UUIDField()
    transaction_date = serializers.DateField()
    is_program_issue = serializers.BooleanField(default=False)
    recipient_name = serializers.CharField(required=False, allow_blank=True, default="")
    reference_document = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    lines = IssueLineSerializer(many=True)


class AdjustmentLineSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    actual_quantity_counted = serializers.DecimalField(max_digits=12, decimal_places=2)
    location_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    batch_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class AdjustStockRequestSerializer(serializers.Serializer):
    warehouse_id = serializers.UUIDField()
    transaction_date = serializers.DateField()
    justification = serializers.CharField()
    reference_document = serializers.CharField(required=False, allow_blank=True, default="")
    lines = AdjustmentLineSerializer(many=True)


class WriteOffLineSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    reason = serializers.CharField(max_length=100)
    location_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    batch_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class WriteOffStockRequestSerializer(serializers.Serializer):
    warehouse_id = serializers.UUIDField()
    transaction_date = serializers.DateField()
    approval_reference = serializers.CharField(max_length=100)
    justification = serializers.CharField()
    lines = WriteOffLineSerializer(many=True)


# ── Stock Response Serializers ────────────────────────────────────────────────


class StockBalanceResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    item_id = serializers.UUIDField()
    item_code = serializers.CharField()
    item_name = serializers.CharField()
    unit_of_measure = serializers.CharField()
    warehouse_id = serializers.UUIDField()
    warehouse_name = serializers.CharField()
    warehouse_code = serializers.CharField()
    location_id = serializers.UUIDField(allow_null=True)
    location_name = serializers.CharField(allow_null=True)
    location_code = serializers.CharField(allow_null=True)
    batch_id = serializers.UUIDField(allow_null=True)
    batch_number = serializers.CharField(allow_null=True)
    expiry_date = serializers.DateField(allow_null=True)
    quantity_on_hand = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_reserved = serializers.DecimalField(max_digits=12, decimal_places=2)
    available_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    reorder_threshold = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_low_stock = serializers.BooleanField()


class StockLedgerResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    transaction_id = serializers.UUIDField()
    transaction_number = serializers.CharField()
    transaction_type = serializers.CharField()
    transaction_date = serializers.DateField()
    item_id = serializers.UUIDField()
    item_code = serializers.CharField()
    item_name = serializers.CharField()
    unit_of_measure = serializers.CharField()
    warehouse_id = serializers.UUIDField()
    warehouse_name = serializers.CharField()
    warehouse_code = serializers.CharField()
    location_id = serializers.UUIDField(allow_null=True)
    location_name = serializers.CharField(allow_null=True)
    batch_id = serializers.UUIDField(allow_null=True)
    batch_number = serializers.CharField(allow_null=True)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    program_id = serializers.UUIDField(allow_null=True)
    activity_id = serializers.UUIDField(allow_null=True)


class TransactionEntryLineResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    item_id = serializers.UUIDField()
    item_code = serializers.CharField()
    item_name = serializers.CharField()
    unit_of_measure = serializers.CharField()
    warehouse_id = serializers.UUIDField()
    warehouse_name = serializers.CharField()
    warehouse_code = serializers.CharField()
    location_id = serializers.UUIDField(allow_null=True)
    location_name = serializers.CharField(allow_null=True)
    batch_id = serializers.UUIDField(allow_null=True)
    batch_number = serializers.CharField(allow_null=True)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    program_id = serializers.UUIDField(allow_null=True)
    activity_id = serializers.UUIDField(allow_null=True)


class TransactionDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    transaction_number = serializers.CharField()
    transaction_type = serializers.CharField()
    status = serializers.CharField()
    transaction_date = serializers.DateField()
    source_warehouse_id = serializers.UUIDField(allow_null=True)
    source_warehouse_name = serializers.CharField(allow_null=True)
    destination_warehouse_id = serializers.UUIDField(allow_null=True)
    destination_warehouse_name = serializers.CharField(allow_null=True)
    executed_by = serializers.UUIDField(allow_null=True)
    reference_document = serializers.CharField()
    donor_name = serializers.CharField()
    notes = serializers.CharField()
    entries = TransactionEntryLineResponseSerializer(many=True)


class ReorderAlertResponseSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    item_code = serializers.CharField()
    item_name = serializers.CharField()
    unit_of_measure = serializers.CharField()
    warehouse_id = serializers.UUIDField()
    warehouse_name = serializers.CharField()
    warehouse_code = serializers.CharField()
    quantity_on_hand = serializers.DecimalField(max_digits=12, decimal_places=2)
    available_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    reorder_threshold = serializers.DecimalField(max_digits=12, decimal_places=2)
    shortage_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)


class ExpiringBatchResponseSerializer(serializers.Serializer):
    batch_id = serializers.UUIDField()
    batch_number = serializers.CharField()
    item_id = serializers.UUIDField()
    item_code = serializers.CharField()
    item_name = serializers.CharField()
    warehouse_id = serializers.UUIDField()
    warehouse_name = serializers.CharField()
    warehouse_code = serializers.CharField()
    expiry_date = serializers.DateField()
    days_until_expiry = serializers.IntegerField()
    quantity_on_hand = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_already_expired = serializers.BooleanField()


class ReceivePurchasedStockLineSerializer(serializers.Serializer):
    po_item_id = serializers.UUIDField()
    item_id = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    location_id = serializers.UUIDField(required=False, allow_null=True)
    batch_id = serializers.UUIDField(required=False, allow_null=True)
    batch_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    expiry_date = serializers.DateField(required=False, allow_null=True)


class ReceivePurchasedStockRequestSerializer(serializers.Serializer):
    warehouse_id = serializers.UUIDField()
    goods_receipt_id = serializers.UUIDField()
    transaction_date = serializers.DateField()
    reference_document = serializers.CharField(max_length=100, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    lines = ReceivePurchasedStockLineSerializer(many=True)


class ReceivePurchasedStockResponseSerializer(serializers.Serializer):
    transaction_id = serializers.UUIDField()
    transaction_number = serializers.CharField()
    goods_receipt_id = serializers.UUIDField()
    goods_receipt_number = serializers.CharField()
    purchase_order_id = serializers.UUIDField()
    purchase_order_number = serializers.CharField()
    total_lines = serializers.IntegerField()
    total_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    destination_warehouse_id = serializers.UUIDField()


class PendingGRNItemResponseSerializer(serializers.Serializer):
    grn_item_id = serializers.UUIDField()
    po_item_id = serializers.UUIDField()
    description = serializers.CharField()
    quantity_received = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_accepted = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_already_received = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity_remaining = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit = serializers.CharField()
    unit_price = serializers.DecimalField(max_digits=15, decimal_places=2)


class PendingGRNResponseSerializer(serializers.Serializer):
    grn_id = serializers.UUIDField()
    receipt_number = serializers.CharField()
    purchase_order_id = serializers.UUIDField()
    purchase_order_number = serializers.CharField()
    vendor_name = serializers.CharField()
    received_date = serializers.DateField()
    total_items = serializers.IntegerField()
    items = PendingGRNItemResponseSerializer(many=True)
