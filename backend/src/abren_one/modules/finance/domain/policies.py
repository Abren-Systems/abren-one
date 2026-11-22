"""Domain policies and invariants for the Finance module."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from abren_one.modules.finance.domain.exceptions import (
    CurrencyMismatchError,
    ImmutableJournalEntryError,
    InvalidJournalLineError,
    UnbalancedJournalEntryError,
)
from abren_one.modules.finance.domain.value_objects import (
    JournalEntryStatus,
)


def validate_journal_lines(
    lines: Sequence[tuple[Decimal, Decimal, str]],
    expected_currency: str | None = None,
) -> tuple[Decimal, Decimal]:
    """Validate journal lines and return (total_debits, total_credits).

    Each line tuple is: (debit, credit, line_currency).
    Invariants:
    1. At least 2 lines required for double-entry bookkeeping.
    2. Each line must have strictly one non-zero side (debit > 0 or credit > 0, never both).
    3. No negative amounts allowed.
    4. All lines must share the expected currency (if provided) and match each other.
    5. Sum of debits must equal sum of credits.
    6. Total amount must be strictly greater than zero.
    """
    if len(lines) < 2:
        raise InvalidJournalLineError(
            "Double-entry bookkeeping requires at least two journal lines (debit and credit)."
        )

    total_debits = Decimal("0.00")
    total_credits = Decimal("0.00")
    common_currency = expected_currency

    for i, (debit, credit, line_currency) in enumerate(lines, start=1):
        if debit < 0 or credit < 0:
            raise InvalidJournalLineError(f"Line {i}: debit and credit amounts cannot be negative.")

        if (debit == 0 and credit == 0) or (debit > 0 and credit > 0):
            raise InvalidJournalLineError(f"Line {i}: exactly one of debit or credit must be greater than zero.")

        if common_currency is None:
            common_currency = line_currency
        elif common_currency != line_currency:
            raise CurrencyMismatchError(
                f"Line {i} currency '{line_currency}' does not match journal currency '{common_currency}'."
            )

        total_debits += debit
        total_credits += credit

    if total_debits <= 0:
        raise InvalidJournalLineError("Journal entry total amount must be greater than zero.")

    if total_debits != total_credits:
        raise UnbalancedJournalEntryError(
            f"Journal entry is unbalanced: total debits ({total_debits}) != total credits ({total_credits})."
        )

    return total_debits, total_credits


def validate_can_post_entry(
    current_status: str,
    total_debits: Decimal,
    total_credits: Decimal,
) -> None:
    """Validate whether a journal entry can transition to POSTED status."""
    if current_status != JournalEntryStatus.DRAFT:
        raise ImmutableJournalEntryError(
            f"Only draft journal entries can be posted. Current status is '{current_status}'."
        )

    if total_debits <= 0 or total_credits <= 0:
        raise InvalidJournalLineError("Journal entry has zero amount.")

    if total_debits != total_credits:
        raise UnbalancedJournalEntryError(
            f"Cannot post unbalanced journal entry: debits={total_debits}, credits={total_credits}."
        )


def validate_can_reverse_entry(
    current_status: str,
    is_already_reversed: bool,
) -> None:
    """Validate whether a journal entry can be reversed."""
    if current_status != JournalEntryStatus.POSTED:
        raise ImmutableJournalEntryError(
            f"Only posted journal entries can be reversed. Current status is '{current_status}'."
        )

    if is_already_reversed:
        raise ImmutableJournalEntryError("This journal entry has already been reversed.")
