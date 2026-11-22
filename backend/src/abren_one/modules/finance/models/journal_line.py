import uuid
from decimal import Decimal

from django.db import models
from django.db.models import Q

from abren_one.modules.finance.domain.exceptions import ImmutableJournalEntryError
from abren_one.modules.finance.domain.value_objects import JournalEntryStatus


class JournalLine(models.Model):
    """An individual debit or credit leg of a journal entry (§4.1, §4.4)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    journal_entry = models.ForeignKey(
        "finance.JournalEntry",
        on_delete=models.CASCADE,
        related_name="lines",
    )
    account = models.ForeignKey(
        "finance.Account",
        on_delete=models.PROTECT,
        related_name="journal_lines",
    )
    debit = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0.00"))
    credit = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0.00"))
    memo = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        db_table = "finance_journal_line"
        ordering = ["journal_entry", "id"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(debit__gt=0, credit=0) | Q(credit__gt=0, debit=0)  # pyright: ignore[reportOperatorIssue]
                ),
                name="finance_line_debit_xor_credit",
            )
        ]

    def __str__(self) -> str:
        if self.debit > 0:
            return f"DR {self.account.code} {self.debit}"
        return f"CR {self.account.code} {self.credit}"

    def delete(self, *args, **kwargs):
        from abren_one.modules.finance.models.journal_entry import JournalEntry

        entry_status = JournalEntry.objects.filter(id=self.journal_entry_id).values_list("status", flat=True).first()
        if entry_status in (
            JournalEntryStatus.POSTED.value,
            JournalEntryStatus.REVERSED.value,
        ):
            raise ImmutableJournalEntryError(
                "Journal lines belonging to a posted or reversed entry cannot be deleted (§4.1, §6.2)."
            )
        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            from abren_one.modules.finance.models.journal_entry import JournalEntry

            entry_status = (
                JournalEntry.objects.filter(id=self.journal_entry_id).values_list("status", flat=True).first()
            )
            if entry_status in (
                JournalEntryStatus.POSTED.value,
                JournalEntryStatus.REVERSED.value,
            ):
                raise ImmutableJournalEntryError(
                    "Journal lines belonging to a posted or reversed entry cannot be modified (§4.1, §6.2)."
                )
        return super().save(*args, **kwargs)
