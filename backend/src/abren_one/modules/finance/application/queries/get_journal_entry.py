from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from abren_one.modules.finance.domain.exceptions import (
    FinanceDomainError,
    JournalEntryNotFoundError,
)
from abren_one.modules.finance.models import JournalEntry
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class JournalLineDetailResult:
    id: UUID
    account_id: UUID
    account_code: str
    account_name: str
    debit: Decimal
    credit: Decimal
    memo: str


@dataclass(frozen=True)
class JournalEntryDetailResult:
    id: UUID
    organization_id: UUID
    entry_number: str
    entry_date: date
    memo: str
    currency: str
    status: str
    posted_at: datetime | None
    posted_by: UUID | None
    source_document: str
    reversal_of_id: UUID | None
    program_id: UUID | None
    grant_id: UUID | None
    donation_id: UUID | None
    lines: list[JournalLineDetailResult]
    total_debits: Decimal
    total_credits: Decimal


def execute(journal_entry_id: UUID, context: ExecutionContext) -> JournalEntryDetailResult:
    """Retrieve full details of a journal entry including its lines (§6.2)."""
    if context.organization_id is None:
        raise FinanceDomainError("Organization context is required.")

    try:
        entry = (
            JournalEntry.objects.select_related("reversal_of")
            .prefetch_related("lines__account")
            .get(id=journal_entry_id, organization_id=context.organization_id)
        )
    except JournalEntry.DoesNotExist as exc:
        raise JournalEntryNotFoundError("Journal entry not found in this organization.") from exc

    line_results = [
        JournalLineDetailResult(
            id=line.id,
            account_id=line.account_id,
            account_code=line.account.code,
            account_name=line.account.name,
            debit=line.debit,
            credit=line.credit,
            memo=line.memo,
        )
        for line in entry.lines.all()
    ]

    total_debits = sum((line.debit for line in line_results), Decimal("0.00"))
    total_credits = sum((line.credit for line in line_results), Decimal("0.00"))

    return JournalEntryDetailResult(
        id=entry.id,
        organization_id=entry.organization_id,
        entry_number=entry.entry_number,
        entry_date=entry.entry_date,
        memo=entry.memo,
        currency=entry.currency,
        status=entry.status,
        posted_at=entry.posted_at,
        posted_by=entry.posted_by,
        source_document=entry.source_document,
        reversal_of_id=entry.reversal_of_id,
        program_id=entry.program_id,
        grant_id=entry.grant_id,
        donation_id=entry.donation_id,
        lines=line_results,
        total_debits=total_debits,
        total_credits=total_credits,
    )
