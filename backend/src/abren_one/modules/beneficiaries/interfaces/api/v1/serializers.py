from decimal import Decimal

from rest_framework import serializers


class RegisterBeneficiaryRequestSerializer(serializers.Serializer):
    beneficiary_type = serializers.ChoiceField(
        choices=["individual", "household", "community"],
        default="individual",
    )
    identification_number = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    household_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    date_of_birth = serializers.DateField(required=False, allow_null=True, default=None)
    gender = serializers.ChoiceField(
        choices=["female", "male", "other", "unspecified"],
        default="unspecified",
    )
    vulnerability_level = serializers.ChoiceField(
        choices=["low", "medium", "high", "critical"],
        default="medium",
    )
    contact_phone = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    contact_address = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class UpdateBeneficiaryRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    household_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=["active", "suspended", "graduated", "archived"],
        required=False,
    )
    vulnerability_level = serializers.ChoiceField(
        choices=["low", "medium", "high", "critical"],
        required=False,
    )
    contact_phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    contact_address = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class BeneficiarySummaryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    beneficiary_type = serializers.CharField()
    identification_number = serializers.CharField()
    display_name = serializers.CharField()
    status = serializers.CharField()
    vulnerability_level = serializers.CharField()
    is_active = serializers.BooleanField()


class BeneficiaryDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    beneficiary_type = serializers.CharField()
    identification_number = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    household_name = serializers.CharField()
    display_name = serializers.CharField()
    date_of_birth = serializers.DateField(allow_null=True)
    gender = serializers.CharField()
    status = serializers.CharField()
    vulnerability_level = serializers.CharField()
    contact_phone = serializers.CharField()
    contact_address = serializers.CharField()
    notes = serializers.CharField()
    is_active = serializers.BooleanField()


class RecordServiceDeliveryRequestSerializer(serializers.Serializer):
    beneficiary_id = serializers.UUIDField()
    service_type = serializers.ChoiceField(
        choices=[
            "food_assistance",
            "medical_support",
            "cash_transfer",
            "education_training",
            "shelter_wash",
            "legal_advocacy",
            "other",
        ]
    )
    delivery_date = serializers.DateField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal("1.00"))
    unit = serializers.CharField(max_length=50, required=False, default="unit")
    program_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    activity_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    status = serializers.ChoiceField(
        choices=["planned", "delivered", "cancelled"],
        default="delivered",
    )


class ServiceDeliveryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    beneficiary_id = serializers.UUIDField()
    beneficiary_name = serializers.CharField()
    service_type = serializers.CharField()
    status = serializers.CharField()
    delivery_date = serializers.DateField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)
    program_id = serializers.UUIDField(allow_null=True)
    activity_id = serializers.UUIDField(allow_null=True)
