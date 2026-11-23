"""Inventory → Finance GL Bridge.

Automatically posts double-entry journal entries to the General Ledger when
inventory operations occur. All cross-module access goes through
``finance.public`` (ADR-006).

Standard Chart of Accounts codes used:
    1200  Inventory Asset
    2010  Accounts Payable – Goods Clearing
    3200  In-Kind Donation Revenue
    5000  General Operational Expenditure
    5100  Program Relief Expenditure
    5800  Inventory Shrinkage / Loss

Failure strategy: if a required GL account code is not found in the
organization's Chart of Accounts, the bridge logs a warning and returns
None — the operational transaction succeeds, but no GL entry is created.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from abren_one.modules.finance.public import (
    AccountByCodeResult,
    AccountNotFoundError,
    CreateJournalEntryInput,
    JournalLineInput,
    create_journal_entry,
    get_account_by_code,
)
from abren_one.platform.common.context import ActorType, ExecutionContext

logger = logging.getLogger(__name__)


# ── Account Code Constants ─────────────────────────────────────────────────

INVENTORY_ASSET_CODE = "1200"
AP_GOODS_CLEARING_CODE = "2010"
IN_KIND_DONATION_REVENUE_CODE = "3200"
GENERAL_EXPENDITURE_CODE = "5000"
PROGRAM_RELIEF_EXPENDITURE_CODE = "5100"
INVENTORY_SHRINKAGE_CODE = "5800"


# ── Shared Helpers ─────────────────────────────────────────────────────────


def _resolve_account(organization_id: UUID, account_code: str) -> AccountByCodeResult | None:
    """Resolve a GL account by code, returning None if not found."""
    try:
        return get_account_by_code(organization_id, account_code)
    except AccountNotFoundError:
        logger.warning(
            "GL bridge: account code '%s' not found for org %s — skipping automatic journal entry.",
            account_code,
            organization_id,
        )
        return None


def _build_system_context(organization_id: UUID) -> ExecutionContext:
    """Build a SYSTEM actor execution context for bridge-initiated GL postings."""
    return ExecutionContext(
        actor_type=ActorType.SYSTEM,
        actor_id=None,
        organization_id=organization_id,
        correlation_id=uuid.uuid4(),
        actor_role="system",
    )


# ── Bridge Functions ───────────────────────────────────────────────────────


@dataclass(frozen=True)
class GLPostingResult:
    """Result of an automatic GL posting attempt."""

    journal_entry_id: UUID | None
    entry_number: str
    posted: bool
    skipped_reason: str


def post_purchase_receipt_gl(
    *,
    organization_id: UUID,
    transaction_number: str,
    total_value: Decimal,
    currency: str,
    entry_date: date,
    goods_receipt_number: str,
    purchase_order_number: str,
) -> GLPostingResult:
    """Post GL entry for goods received from a purchase order.

    Dr  1200  Inventory Asset                total_value
    Cr  2010  Accounts Payable – Clearing    total_value
    """
    inv_account = _resolve_account(organization_id, INVENTORY_ASSET_CODE)
    ap_account = _resolve_account(organization_id, AP_GOODS_CLEARING_CODE)

    if inv_account is None or ap_account is None:
        return GLPostingResult(
            journal_entry_id=None,
            entry_number="",
            posted=False,
            skipped_reason="Required GL accounts not configured (1200, 2010).",
        )

    ctx = _build_system_context(organization_id)
    result = create_journal_entry(
        CreateJournalEntryInput(
            context=ctx,
            entry_date=entry_date,
            memo=(
                f"Auto-GL: Purchased stock receipt {transaction_number} "
                f"(GRN {goods_receipt_number}, PO {purchase_order_number})"
            ),
            currency=currency,
            lines=[
                JournalLineInput(
                    account_id=inv_account.id,
                    debit=total_value,
                    credit=Decimal("0.00"),
                    memo=f"Stock in: {transaction_number}",
                ),
                JournalLineInput(
                    account_id=ap_account.id,
                    debit=Decimal("0.00"),
                    credit=total_value,
                    memo=f"AP clearing: {goods_receipt_number}",
                ),
            ],
            source_document=transaction_number,
            post_immediately=True,
        )
    )

    logger.info(
        "GL bridge: posted purchase receipt JE %s (Dr 1200 / Cr 2010 = %s %s) for inventory txn %s.",
        result.entry_number,
        total_value,
        currency,
        transaction_number,
    )
    return GLPostingResult(
        journal_entry_id=result.journal_entry_id,
        entry_number=result.entry_number,
        posted=True,
        skipped_reason="",
    )


def post_stock_issue_gl(
    *,
    organization_id: UUID,
    transaction_number: str,
    total_value: Decimal,
    currency: str,
    entry_date: date,
    is_program_issue: bool,
) -> GLPostingResult:
    """Post GL entry for stock issued out of warehouse.

    Program issue:
        Dr  5100  Program Relief Expenditure    total_value
        Cr  1200  Inventory Asset               total_value

    General issue:
        Dr  5000  General Operational Expenditure  total_value
        Cr  1200  Inventory Asset                  total_value
    """
    inv_account = _resolve_account(organization_id, INVENTORY_ASSET_CODE)
    expense_code = PROGRAM_RELIEF_EXPENDITURE_CODE if is_program_issue else GENERAL_EXPENDITURE_CODE
    expense_account = _resolve_account(organization_id, expense_code)

    if inv_account is None or expense_account is None:
        return GLPostingResult(
            journal_entry_id=None,
            entry_number="",
            posted=False,
            skipped_reason=f"Required GL accounts not configured (1200, {expense_code}).",
        )

    issue_type = "program" if is_program_issue else "general"
    ctx = _build_system_context(organization_id)
    result = create_journal_entry(
        CreateJournalEntryInput(
            context=ctx,
            entry_date=entry_date,
            memo=f"Auto-GL: {issue_type.capitalize()} stock issue {transaction_number}",
            currency=currency,
            lines=[
                JournalLineInput(
                    account_id=expense_account.id,
                    debit=total_value,
                    credit=Decimal("0.00"),
                    memo=f"{issue_type.capitalize()} expenditure: {transaction_number}",
                ),
                JournalLineInput(
                    account_id=inv_account.id,
                    debit=Decimal("0.00"),
                    credit=total_value,
                    memo=f"Stock out: {transaction_number}",
                ),
            ],
            source_document=transaction_number,
            post_immediately=True,
        )
    )

    logger.info(
        "GL bridge: posted %s issue JE %s (Dr %s / Cr 1200 = %s %s) for inventory txn %s.",
        issue_type,
        result.entry_number,
        expense_code,
        total_value,
        currency,
        transaction_number,
    )
    return GLPostingResult(
        journal_entry_id=result.journal_entry_id,
        entry_number=result.entry_number,
        posted=True,
        skipped_reason="",
    )


def post_write_off_gl(
    *,
    organization_id: UUID,
    transaction_number: str,
    total_value: Decimal,
    currency: str,
    entry_date: date,
    approval_reference: str,
) -> GLPostingResult:
    """Post GL entry for stock write-off (damage, expiry, loss).

    Dr  5800  Inventory Shrinkage / Loss     total_value
    Cr  1200  Inventory Asset                total_value
    """
    inv_account = _resolve_account(organization_id, INVENTORY_ASSET_CODE)
    shrinkage_account = _resolve_account(organization_id, INVENTORY_SHRINKAGE_CODE)

    if inv_account is None or shrinkage_account is None:
        return GLPostingResult(
            journal_entry_id=None,
            entry_number="",
            posted=False,
            skipped_reason="Required GL accounts not configured (1200, 5800).",
        )

    ctx = _build_system_context(organization_id)
    result = create_journal_entry(
        CreateJournalEntryInput(
            context=ctx,
            entry_date=entry_date,
            memo=(f"Auto-GL: Stock write-off {transaction_number} (Approval: {approval_reference})"),
            currency=currency,
            lines=[
                JournalLineInput(
                    account_id=shrinkage_account.id,
                    debit=total_value,
                    credit=Decimal("0.00"),
                    memo=f"Write-off loss: {transaction_number}",
                ),
                JournalLineInput(
                    account_id=inv_account.id,
                    debit=Decimal("0.00"),
                    credit=total_value,
                    memo=f"Inventory disposed: {transaction_number}",
                ),
            ],
            source_document=transaction_number,
            post_immediately=True,
        )
    )

    logger.info(
        "GL bridge: posted write-off JE %s (Dr 5800 / Cr 1200 = %s %s) for inventory txn %s.",
        result.entry_number,
        total_value,
        currency,
        transaction_number,
    )
    return GLPostingResult(
        journal_entry_id=result.journal_entry_id,
        entry_number=result.entry_number,
        posted=True,
        skipped_reason="",
    )


def post_in_kind_donation_gl(
    *,
    organization_id: UUID,
    transaction_number: str,
    total_fair_value: Decimal,
    currency: str,
    entry_date: date,
    donor_name: str,
) -> GLPostingResult:
    """Post GL entry for in-kind donation received into inventory.

    Dr  1200  Inventory Asset                total_fair_value
    Cr  3200  In-Kind Donation Revenue       total_fair_value
    """
    inv_account = _resolve_account(organization_id, INVENTORY_ASSET_CODE)
    revenue_account = _resolve_account(organization_id, IN_KIND_DONATION_REVENUE_CODE)

    if inv_account is None or revenue_account is None:
        return GLPostingResult(
            journal_entry_id=None,
            entry_number="",
            posted=False,
            skipped_reason="Required GL accounts not configured (1200, 3200).",
        )

    ctx = _build_system_context(organization_id)
    result = create_journal_entry(
        CreateJournalEntryInput(
            context=ctx,
            entry_date=entry_date,
            memo=(f"Auto-GL: In-kind donation from {donor_name} ({transaction_number})"),
            currency=currency,
            lines=[
                JournalLineInput(
                    account_id=inv_account.id,
                    debit=total_fair_value,
                    credit=Decimal("0.00"),
                    memo=f"In-kind stock in: {transaction_number}",
                ),
                JournalLineInput(
                    account_id=revenue_account.id,
                    debit=Decimal("0.00"),
                    credit=total_fair_value,
                    memo=f"Donation revenue: {donor_name}",
                ),
            ],
            source_document=transaction_number,
            post_immediately=True,
        )
    )

    logger.info(
        "GL bridge: posted in-kind donation JE %s (Dr 1200 / Cr 3200 = %s %s) for inventory txn %s from %s.",
        result.entry_number,
        total_fair_value,
        currency,
        transaction_number,
        donor_name,
    )
    return GLPostingResult(
        journal_entry_id=result.journal_entry_id,
        entry_number=result.entry_number,
        posted=True,
        skipped_reason="",
    )
