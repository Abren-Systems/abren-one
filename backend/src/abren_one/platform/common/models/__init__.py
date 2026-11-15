from django.db import models


class TimestampMixin(models.Model):
    """Base mixin providing automatic created_at and updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OrgOwnedMixin(models.Model):
    """Records that belong to a specific organization.

    Note: Uses `related_name="+"` intentionally (§3.1, §4.4).
    In a modular monolith, business modules must not access other modules'
    entities via reverse ORM relationships (which would bypass public.py).
    Disabling reverse relationships ensures strict module encapsulation.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="+",
    )

    class Meta:
        abstract = True


__all__ = ["OrgOwnedMixin", "TimestampMixin"]
