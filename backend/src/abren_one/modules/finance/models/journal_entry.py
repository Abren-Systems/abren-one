import uuid

from django.db import models

from abren_one.modules.finance.domain.value_objects import JournalEntryStatus
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class JournalEntry(OrgOwnedMixin, TimestampMixin, models.Model):
    """A balanced accounting journal entry in the general ledger (§4.1, §4.4)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entry_number = models.CharField(max_length=100)
    entry_date = models.DateField(db_index=True)
    memo = models.TextField(blank=True, default="")
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(
        max_length=30,
        choices=[(s.value, s.name) for s in JournalEntryStatus],
        default=JournalEntryStatus.DRAFT.value,
        db_index=True,
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.UUIDField(null=True, blank=True)
    source_document = models.CharField(max_length=255, blank=True, default="")
    reversal_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reversed_by_entries",
    )

    # Soft cross-module references (§4.4)
    program_id = models.UUIDField(null=True, blank=True, db_index=True)
    grant_id = models.UUIDField(null=True, blank=True, db_index=True)
    donation_id = models.UUIDField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "finance_journal_entry"
        ordering = ["-entry_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "entry_number"],
                name="unique_journal_entry_number_per_org",
            )
        ]

    def __str__(self) -> str:
        return f"{self.entry_number} [{self.status}] {self.memo[:40]}"
