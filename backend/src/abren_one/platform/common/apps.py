from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "abren_one.platform.common"
    label = "common"
    verbose_name = "Common Platform"
