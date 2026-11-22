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
