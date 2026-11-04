from django.db import models


class TimestampMixin(models.Model):
    """Base mixin providing automatic created_at and updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OrgOwnedMixin(models.Model):
    """Records that belong to a specific organization."""

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="+",
    )

    class Meta:
        abstract = True


__all__ = ["OrgOwnedMixin", "TimestampMixin"]
