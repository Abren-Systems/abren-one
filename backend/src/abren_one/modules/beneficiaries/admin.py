from django.contrib import admin

from abren_one.modules.beneficiaries.models import Beneficiary, ServiceDelivery


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "beneficiary_type",
        "organization",
        "status",
        "vulnerability_level",
        "created_at",
    )
    list_filter = ("status", "beneficiary_type", "vulnerability_level", "organization")
    search_fields = (
        "first_name",
        "last_name",
        "household_name",
        "identification_number",
        "contact_phone",
        "organization__name",
    )
    ordering = ("-created_at",)


@admin.register(ServiceDelivery)
class ServiceDeliveryAdmin(admin.ModelAdmin):
    list_display = (
        "service_type",
        "beneficiary",
        "organization",
        "quantity",
        "unit",
        "status",
        "delivery_date",
    )
    list_filter = ("service_type", "status", "organization")
    search_fields = (
        "beneficiary__first_name",
        "beneficiary__last_name",
        "beneficiary__household_name",
        "organization__name",
    )
    ordering = ("-delivery_date", "-created_at")
