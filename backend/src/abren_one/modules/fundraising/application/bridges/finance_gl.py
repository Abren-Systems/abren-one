"""Fundraising → Finance GL Bridge.

Automatically posts double-entry journal entries to the General Ledger when
fundraising events occur. All cross-module access goes through
``finance.public`` (ADR-006).

Standard Chart of Accounts codes used:
    1010  Cash / Bank
    3100  Donor Revenue – Temporarily Restricted

Failure strategy: graceful degradation — if GL accounts are not configured,
the donation is still recorded but no GL entry is created.
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

CASH_BANK_CODE = "1010"
DONOR_REVENUE_RESTRICTED_CODE = "3100"


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


def post_donation_received_gl(
    *,
    organization_id: UUID,
    donation_id: UUID,
    donor_name: str,
    amount: Decimal,
    currency: str,
    received_date: date,
    grant_id: UUID | None = None,
    reference: str = "",
) -> GLPostingResult:
    """Post GL entry for a monetary donation received.

    Dr  1010  Cash / Bank                           amount
    Cr  3100  Donor Revenue – Temporarily Restricted amount
    """
    cash_account = _resolve_account(organization_id, CASH_BANK_CODE)
    revenue_account = _resolve_account(organization_id, DONOR_REVENUE_RESTRICTED_CODE)

    if cash_account is None or revenue_account is None:
        return GLPostingResult(
            journal_entry_id=None,
            entry_number="",
            posted=False,
            skipped_reason="Required GL accounts not configured (1010, 3100).",
        )

    source_doc = reference or str(donation_id)
    grant_memo = " (Grant-linked)" if grant_id else ""

    ctx = _build_system_context(organization_id)
    result = create_journal_entry(
        CreateJournalEntryInput(
            context=ctx,
            entry_date=received_date,
            memo=(f"Auto-GL: Donation received from {donor_name}{grant_memo} — {source_doc}"),
            currency=currency,
            lines=[
                JournalLineInput(
                    account_id=cash_account.id,
                    debit=amount,
                    credit=Decimal("0.00"),
                    memo=f"Cash in: donation from {donor_name}",
                ),
                JournalLineInput(
                    account_id=revenue_account.id,
                    debit=Decimal("0.00"),
                    credit=amount,
                    memo=f"Donor revenue: {donor_name}",
                ),
            ],
            source_document=source_doc,
            donation_id=donation_id,
            grant_id=grant_id,
            post_immediately=True,
        )
    )

    logger.info(
        "GL bridge: posted donation JE %s (Dr 1010 / Cr 3100 = %s %s) for donation %s from %s.",
        result.entry_number,
        amount,
        currency,
        donation_id,
        donor_name,
    )
    return GLPostingResult(
        journal_entry_id=result.journal_entry_id,
        entry_number=result.entry_number,
        posted=True,
        skipped_reason="",
    )
