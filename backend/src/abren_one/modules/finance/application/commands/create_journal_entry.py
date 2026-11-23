from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from abren_one.modules.finance.application.number_generation import (
    generate_journal_entry_number,
)
from abren_one.modules.finance.domain.exceptions import (
    AccountNotFoundError,
    FinanceDomainError,
)
from abren_one.modules.finance.domain.policies import validate_journal_lines
from abren_one.modules.finance.domain.value_objects import JournalEntryStatus
from abren_one.modules.finance.models import Account, JournalEntry, JournalLine
from abren_one.modules.fundraising.public import (
    DonationNotFoundError,
    GrantNotFoundError,
    get_donation,
    get_grant,
)
from abren_one.modules.organizations.public import get_organization
from abren_one.modules.programs.public import ProgramNotFoundError, get_program
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.authorization import check_permission
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class JournalLineInput:
    account_id: UUID
    debit: Decimal = Decimal("0.00")
    credit: Decimal = Decimal("0.00")
    memo: str = ""


@dataclass(frozen=True)
class CreateJournalEntryInput:
    context: ExecutionContext
    entry_date: date
    memo: str
    currency: str = "USD"
    lines: Sequence[JournalLineInput] = ()
    entry_number: str = ""
    source_document: str = ""
    program_id: UUID | None = None
    grant_id: UUID | None = None
    donation_id: UUID | None = None
    post_immediately: bool = False


@dataclass(frozen=True)
class CreateJournalEntryResult:
    journal_entry_id: UUID
    entry_number: str
    status: str
    total_debits: Decimal
    total_credits: Decimal


@transaction.atomic
def execute(data: CreateJournalEntryInput) -> CreateJournalEntryResult:
    """Create a journal entry (draft or posted immediately) with balanced lines."""
    check_permission(data.context, "finance:journal_entries:create")
    if data.post_immediately:
        check_permission(data.context, "finance:journal_entries:post")

    if data.context.organization_id is None:
        raise FinanceDomainError("Organization context is required.")

    org = get_organization(organization_id=data.context.organization_id)
    if not org.is_active:
        raise FinanceDomainError("Cannot create journal entry for an inactive or suspended organization.")

    # Validate soft cross-module references against active tenant (§4.4)
    if data.program_id:
        try:
            get_program(organization_id=org.id, program_id=data.program_id)
        except ProgramNotFoundError as exc:
            raise FinanceDomainError(f"Program {data.program_id} not found in this organization.") from exc

    if data.grant_id:
        try:
            get_grant(grant_id=data.grant_id, organization_id=org.id)
        except GrantNotFoundError as exc:
            raise FinanceDomainError(f"Grant {data.grant_id} not found in this organization.") from exc

    if data.donation_id:
        try:
            get_donation(donation_id=data.donation_id, organization_id=org.id)
        except DonationNotFoundError as exc:
            raise FinanceDomainError(f"Donation {data.donation_id} not found in this organization.") from exc

    currency = data.currency.upper()

    # Load and validate accounts with lock in canonical order to avoid deadlock
    account_ids = {line.account_id for line in data.lines}
    accounts_by_id = {
        acc.id: acc
        for acc in Account.objects.select_for_update()
        .filter(id__in=sorted(account_ids), organization_id=org.id)
        .order_by("id")
    }

    if len(accounts_by_id) != len(account_ids):
        missing = account_ids - set(accounts_by_id.keys())
        raise AccountNotFoundError(f"Accounts not found in this organization: {missing}")

    # Validate lines according to domain policy
    line_tuples = [
        (
            Decimal(str(line.debit)),
            Decimal(str(line.credit)),
            accounts_by_id[line.account_id].currency,
        )
        for line in data.lines
    ]
    total_debits, total_credits = validate_journal_lines(
        line_tuples,
        expected_currency=currency,
    )

    entry_num = data.entry_number.strip()
    if not entry_num:
        entry_num = generate_journal_entry_number(org.id, data.entry_date)
    elif JournalEntry.objects.filter(organization_id=org.id, entry_number=entry_num).exists():
        raise FinanceDomainError(f"Journal entry number '{entry_num}' already exists.")

    status = JournalEntryStatus.POSTED.value if data.post_immediately else JournalEntryStatus.DRAFT.value
    now = timezone.now() if data.post_immediately else None
    posted_by = data.context.actor_id if data.post_immediately else None

    entry = JournalEntry.objects.create(
        organization_id=org.id,
        entry_number=entry_num,
        entry_date=data.entry_date,
        memo=data.memo.strip(),
        currency=currency,
        status=status,
        posted_at=now,
        posted_by=posted_by,
        source_document=data.source_document.strip(),
        program_id=data.program_id,
        grant_id=data.grant_id,
        donation_id=data.donation_id,
    )

    lines_to_create = [
        JournalLine(
            journal_entry=entry,
            account=accounts_by_id[line.account_id],
            debit=Decimal(str(line.debit)),
            credit=Decimal(str(line.credit)),
            memo=line.memo.strip(),
        )
        for line in data.lines
    ]
    JournalLine.objects.bulk_create(lines_to_create)

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        actor_role=data.context.actor_role,
        organization_id=org.id,
        action="finance.journal_entry.created",
        target_type="finance.JournalEntry",
        target_id=entry.id,
        correlation_id=data.context.correlation_id,
        metadata={
            "entry_number": entry.entry_number,
            "status": entry.status,
            "total_debits": str(total_debits),
            "total_credits": str(total_credits),
            "currency": currency,
        },
    )

    if data.post_immediately:
        record_audit_event(
            actor_type=data.context.actor_type.value,
            actor_id=data.context.actor_id,
            actor_role=data.context.actor_role,
            organization_id=org.id,
            action="finance.journal_entry.posted",
            target_type="finance.JournalEntry",
            target_id=entry.id,
            correlation_id=data.context.correlation_id,
            metadata={"entry_number": entry.entry_number, "posted_at": now.isoformat() if now else None},
        )

    return CreateJournalEntryResult(
        journal_entry_id=entry.id,
        entry_number=entry.entry_number,
        status=entry.status,
        total_debits=total_debits,
        total_credits=total_credits,
    )
