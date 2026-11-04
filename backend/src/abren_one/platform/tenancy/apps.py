from django.apps import AppConfig


class TenancyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "abren_one.platform.tenancy"
    label = "tenancy"
    verbose_name = "Tenancy"
