from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "abren_one.platform.audit"
    label = "audit"
    verbose_name = "Audit"
