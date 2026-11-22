import uuid

from django.db import models

from abren_one.modules.finance.domain.value_objects import AccountType
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class Account(OrgOwnedMixin, TimestampMixin, models.Model):
    """An account in the Chart of Accounts (§4.1, §4.4)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    account_type = models.CharField(
        max_length=30,
        choices=[(t.value, t.name) for t in AccountType],
        default=AccountType.ASSET.value,
        db_index=True,
    )
    currency = models.CharField(max_length=3, default="USD")
    is_active = models.BooleanField(default=True, db_index=True)
    description = models.TextField(blank=True, default="")
    parent = models.ForeignKey(
        "self",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        db_table = "finance_account"
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_account_code_per_org",
            )
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name} ({self.account_type})"
