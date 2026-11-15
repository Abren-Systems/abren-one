from rest_framework import serializers


class CreateDonorRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    donor_type = serializers.CharField(max_length=50, required=False, default="individual")
    email = serializers.EmailField(required=False, default="", allow_blank=True)
    phone = serializers.CharField(max_length=50, required=False, default="", allow_blank=True)


class DonorResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    name = serializers.CharField()
    donor_type = serializers.CharField()
    email = serializers.CharField()
    phone = serializers.CharField(required=False)
    status = serializers.CharField()
    is_active = serializers.BooleanField()


class CreateGrantRequestSerializer(serializers.Serializer):
    donor_id = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    reference_code = serializers.CharField(max_length=100)
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    currency = serializers.CharField(max_length=3, required=False, default="USD")
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    program_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class GrantResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    donor_id = serializers.UUIDField()
    title = serializers.CharField()
    reference_code = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    currency = serializers.CharField()
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    status = serializers.CharField()
    is_active = serializers.BooleanField()
    program_id = serializers.UUIDField(allow_null=True, required=False)


class RecordDonationRequestSerializer(serializers.Serializer):
    donor_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    currency = serializers.CharField(max_length=3, required=False, default="USD")
    payment_method = serializers.CharField(max_length=50, required=False, default="bank_transfer")
    reference = serializers.CharField(max_length=100, required=False, default="", allow_blank=True)
    grant_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    program_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    received_at = serializers.DateTimeField(required=False, allow_null=True, default=None)


class DonationResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    donor_id = serializers.UUIDField()
    donor_name = serializers.CharField()
    grant_id = serializers.UUIDField(allow_null=True)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    currency = serializers.CharField()
    received_at = serializers.DateTimeField()
    payment_method = serializers.CharField()
    status = serializers.CharField()
    program_id = serializers.UUIDField(allow_null=True)
