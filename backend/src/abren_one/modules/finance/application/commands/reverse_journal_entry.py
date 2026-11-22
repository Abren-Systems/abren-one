from dataclasses import dataclass
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from abren_one.modules.finance.domain.exceptions import (
    FinanceDomainError,
    JournalEntryNotFoundError,
)
from abren_one.modules.finance.domain.policies import validate_can_reverse_entry
from abren_one.modules.finance.domain.value_objects import JournalEntryStatus
from abren_one.modules.finance.models import JournalEntry, JournalLine
from abren_one.modules.organizations.public import get_organization
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class ReverseJournalEntryInput:
    context: ExecutionContext
    journal_entry_id: UUID
    reason: str


@dataclass(frozen=True)
class ReverseJournalEntryResult:
    original_entry_id: UUID
    original_entry_number: str
    reversal_entry_id: UUID
    reversal_entry_number: str
    reversed_at: str


@transaction.atomic
def execute(data: ReverseJournalEntryInput) -> ReverseJournalEntryResult:
    """Reverse a posted journal entry with an offsetting, balanced reversal entry (§6.2)."""
    if data.context.organization_id is None:
        raise FinanceDomainError("Organization context is required.")

    org = get_organization(organization_id=data.context.organization_id)
    if not org.is_active:
        raise FinanceDomainError("Cannot reverse journal entry for an inactive or suspended organization.")

    reason = data.reason.strip()
    if not reason:
        raise FinanceDomainError("A reason is required to reverse a journal entry.")

    try:
        original = (
            JournalEntry.objects.select_for_update()
            .prefetch_related("lines")
            .get(id=data.journal_entry_id, organization_id=org.id)
        )
    except JournalEntry.DoesNotExist as exc:
        raise JournalEntryNotFoundError("Journal entry not found in this organization.") from exc

    has_reversal = JournalEntry.objects.filter(reversal_of=original).exists()
    validate_can_reverse_entry(
        current_status=original.status,
        is_already_reversed=has_reversal,
    )

    now = timezone.now()
    reversal_entry_num = f"REV-{original.entry_number}"
    reversal_memo = f"Reversal of {original.entry_number}: {reason}"

    # Create the reversal entry with inverted lines
    reversal_entry = JournalEntry.objects.create(
        organization_id=org.id,
        entry_number=reversal_entry_num,
        entry_date=now.date(),
        memo=reversal_memo,
        currency=original.currency,
        status=JournalEntryStatus.POSTED.value,
        posted_at=now,
        posted_by=data.context.actor_id,
        source_document=f"Reversal of {original.entry_number}",
        reversal_of=original,
        program_id=original.program_id,
        grant_id=original.grant_id,
        donation_id=original.donation_id,
    )

    # Invert debits and credits
    reversal_lines = [
        JournalLine(
            journal_entry=reversal_entry,
            account=line.account,
            debit=line.credit,  # inverted
            credit=line.debit,  # inverted
            memo=f"Offsetting {line.account.code}",
        )
        for line in original.lines.all()
    ]
    JournalLine.objects.bulk_create(reversal_lines)

    # Mark original as REVERSED
    original.status = JournalEntryStatus.REVERSED.value
    original.save(update_fields=["status", "updated_at"])

    # Audit both actions
    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=org.id,
        action="finance.journal_entry.reversed",
        target_type="finance.JournalEntry",
        target_id=original.id,
        correlation_id=data.context.correlation_id,
        metadata={
            "entry_number": original.entry_number,
            "reversal_entry_number": reversal_entry.entry_number,
            "reason": reason,
        },
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=org.id,
        action="finance.journal_entry.created",
        target_type="finance.JournalEntry",
        target_id=reversal_entry.id,
        correlation_id=data.context.correlation_id,
        metadata={
            "entry_number": reversal_entry.entry_number,
            "status": reversal_entry.status,
            "reversal_of": original.entry_number,
        },
    )

    return ReverseJournalEntryResult(
        original_entry_id=original.id,
        original_entry_number=original.entry_number,
        reversal_entry_id=reversal_entry.id,
        reversal_entry_number=reversal_entry.entry_number,
        reversed_at=now.isoformat(),
    )
