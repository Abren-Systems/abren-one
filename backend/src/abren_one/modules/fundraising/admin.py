from django.contrib import admin

from abren_one.modules.fundraising.models import Donation, Donor, Grant


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "donor_type", "email", "status", "created_at")
    list_filter = ("donor_type", "status", "organization")
    search_fields = ("name", "email", "organization__name")
    ordering = ("name",)


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "organization",
        "donor",
        "reference_code",
        "total_amount",
        "currency",
        "status",
        "start_date",
        "end_date",
    )
    list_filter = ("status", "currency", "organization")
    search_fields = ("title", "reference_code", "donor__name")
    ordering = ("-start_date",)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organization",
        "donor",
        "grant",
        "amount",
        "currency",
        "payment_method",
        "status",
        "received_at",
    )
    list_filter = ("status", "payment_method", "currency", "organization")
    search_fields = ("reference", "donor__name", "grant__title")
    ordering = ("-received_at",)
