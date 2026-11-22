from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.db.models import Sum

from abren_one.modules.finance.domain.exceptions import FinanceDomainError
from abren_one.modules.finance.domain.value_objects import (
    AccountType,
    JournalEntryStatus,
)
from abren_one.modules.finance.models import Account, JournalLine
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class TrialBalanceItem:
    account_id: UUID
    code: str
    name: str
    account_type: str
    normal_balance: str
    total_debit: Decimal
    total_credit: Decimal
    balance_debit: Decimal
    balance_credit: Decimal


@dataclass(frozen=True)
class TrialBalanceResult:
    items: list[TrialBalanceItem]
    total_debits: Decimal
    total_credits: Decimal
    is_balanced: bool
    currency: str


def execute(context: ExecutionContext, currency: str = "USD") -> TrialBalanceResult:
    """Calculate the Trial Balance from all posted journal entries for the active organization (§6.2)."""
    if context.organization_id is None:
        raise FinanceDomainError("Organization context is required.")

    curr = currency.upper()
    accounts = Account.objects.filter(
        organization_id=context.organization_id,
        currency=curr,
    ).order_by("code")

    items: list[TrialBalanceItem] = []
    total_tb_debits = Decimal("0.00")
    total_tb_credits = Decimal("0.00")

    for acc in accounts:
        # Sum debits and credits from POSTED and REVERSED journal entries
        aggregates = JournalLine.objects.filter(
            account=acc,
            journal_entry__organization_id=context.organization_id,
            journal_entry__status__in=[
                JournalEntryStatus.POSTED.value,
                JournalEntryStatus.REVERSED.value,
            ],
        ).aggregate(
            sum_debit=Sum("debit"),
            sum_credit=Sum("credit"),
        )

        sum_debit = aggregates["sum_debit"] or Decimal("0.00")
        sum_credit = aggregates["sum_credit"] or Decimal("0.00")

        # Skip zero-balance inactive accounts
        if sum_debit == 0 and sum_credit == 0:
            continue

        acc_type = AccountType(acc.account_type)
        normal = acc_type.normal_balance

        net = sum_debit - sum_credit
        if net >= 0:
            bal_debit = net
            bal_credit = Decimal("0.00")
        else:
            bal_debit = Decimal("0.00")
            bal_credit = -net

        items.append(
            TrialBalanceItem(
                account_id=acc.id,
                code=acc.code,
                name=acc.name,
                account_type=acc.account_type,
                normal_balance=normal.value,
                total_debit=sum_debit,
                total_credit=sum_credit,
                balance_debit=bal_debit,
                balance_credit=bal_credit,
            )
        )

        total_tb_debits += bal_debit
        total_tb_credits += bal_credit

    is_balanced = total_tb_debits == total_tb_credits

    return TrialBalanceResult(
        items=items,
        total_debits=total_tb_debits,
        total_credits=total_tb_credits,
        is_balanced=is_balanced,
        currency=curr,
    )
