from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db.models import Sum

from abren_one.modules.finance.domain.exceptions import FinanceDomainError
from abren_one.modules.finance.models import JournalEntry
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class JournalEntrySummaryResult:
    id: UUID
    entry_number: str
    entry_date: date
    memo: str
    currency: str
    status: str
    total_amount: Decimal
    reversal_of_id: UUID | None


def execute(
    context: ExecutionContext,
    status: str | None = None,
) -> list[JournalEntrySummaryResult]:
    """List journal entries for the active organization (§6.2)."""
    if context.organization_id is None:
        raise FinanceDomainError("Organization context is required.")

    qs = JournalEntry.objects.filter(organization_id=context.organization_id)
    if status:
        qs = qs.filter(status=status)

    entries = qs.annotate(total_debits=Sum("lines__debit")).order_by("-entry_date", "-created_at")

    return [
        JournalEntrySummaryResult(
            id=entry.id,
            entry_number=entry.entry_number,
            entry_date=entry.entry_date,
            memo=entry.memo,
            currency=entry.currency,
            status=entry.status,
            total_amount=entry.total_debits or Decimal("0.00"),  # type: ignore
            reversal_of_id=entry.reversal_of_id,
        )
        for entry in entries
    ]
