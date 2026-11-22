from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from abren_one.modules.finance.domain.exceptions import (
    FinanceDomainError,
    JournalEntryNotFoundError,
)
from abren_one.modules.finance.domain.policies import validate_can_post_entry
from abren_one.modules.finance.domain.value_objects import JournalEntryStatus
from abren_one.modules.finance.models import JournalEntry
from abren_one.modules.organizations.public import get_organization
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class PostJournalEntryInput:
    context: ExecutionContext
    journal_entry_id: UUID


@dataclass(frozen=True)
class PostJournalEntryResult:
    journal_entry_id: UUID
    entry_number: str
    status: str
    posted_at: str


@transaction.atomic
def execute(data: PostJournalEntryInput) -> PostJournalEntryResult:
    """Post a draft journal entry to the general ledger (§6.2)."""
    check_permission(data.context, "finance:journal_entries:post")

    if data.context.organization_id is None:
        raise FinanceDomainError("Organization context is required.")

    org = get_organization(organization_id=data.context.organization_id)
    if not org.is_active:
        raise FinanceDomainError("Cannot post journal entry for an inactive or suspended organization.")

    try:
        entry = (
            JournalEntry.objects.select_for_update()
            .prefetch_related("lines")
            .get(id=data.journal_entry_id, organization_id=org.id)
        )
    except JournalEntry.DoesNotExist as exc:
        raise JournalEntryNotFoundError("Journal entry not found in this organization.") from exc

    lines = list(entry.lines.all())
    total_debits = sum((line.debit for line in lines), Decimal("0.00"))
    total_credits = sum((line.credit for line in lines), Decimal("0.00"))

    validate_can_post_entry(
        current_status=entry.status,
        total_debits=total_debits,
        total_credits=total_credits,
    )

    now = timezone.now()
    entry.status = JournalEntryStatus.POSTED.value
    entry.posted_at = now
    entry.posted_by = data.context.actor_id
    entry.save(update_fields=["status", "posted_at", "posted_by", "updated_at"])

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=org.id,
        action="finance.journal_entry.posted",
        target_type="finance.JournalEntry",
        target_id=entry.id,
        correlation_id=data.context.correlation_id,
        metadata={
            "entry_number": entry.entry_number,
            "posted_at": now.isoformat(),
            "total_debits": str(total_debits),
            "total_credits": str(total_credits),
        },
    )

    return PostJournalEntryResult(
        journal_entry_id=entry.id,
        entry_number=entry.entry_number,
        status=entry.status,
        posted_at=now.isoformat(),
    )
