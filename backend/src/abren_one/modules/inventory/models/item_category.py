import uuid

from django.db import models

from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class ItemCategory(OrgOwnedMixin, TimestampMixin, models.Model):
    """Hierarchical classification for stock-tracked items."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, default="")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        db_table = "inventory_item_category"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_item_category_code_per_org",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
