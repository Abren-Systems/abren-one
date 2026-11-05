from django.contrib import admin

from abren_one.modules.organizations.models import (
    Branch,
    Department,
    Membership,
    Organization,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "status", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("status",)
    ordering = ("name",)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "organization", "is_headquarters", "is_active")
    search_fields = ("name", "code", "organization__name")
    list_filter = ("is_active", "is_headquarters")
    ordering = ("organization", "name")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "organization", "branch", "is_active")
    search_fields = ("name", "code", "organization__name")
    list_filter = ("is_active",)
    ordering = ("organization", "name")


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "role", "status", "created_at")
    search_fields = ("user__username", "user__email", "organization__name")
    list_filter = ("role", "status")
    ordering = ("organization", "-created_at")
