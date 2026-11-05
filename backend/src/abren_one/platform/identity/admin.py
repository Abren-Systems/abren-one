from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from abren_one.platform.identity.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""

    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
