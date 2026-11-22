"""Unit tests for Finance domain policies and invariants."""

from decimal import Decimal

import pytest

from abren_one.modules.finance.domain.exceptions import (
    CurrencyMismatchError,
    ImmutableJournalEntryError,
    InvalidJournalLineError,
    UnbalancedJournalEntryError,
)
from abren_one.modules.finance.domain.policies import (
    validate_can_post_entry,
    validate_can_reverse_entry,
    validate_journal_lines,
)
from abren_one.modules.finance.domain.value_objects import (
    AccountType,
    JournalEntryStatus,
    NormalBalance,
)


class TestAccountTypeNormals:
    def test_asset_and_expense_are_normal_debit(self):
        assert AccountType.ASSET.normal_balance == NormalBalance.DEBIT
        assert AccountType.EXPENSE.normal_balance == NormalBalance.DEBIT

    def test_liability_equity_revenue_are_normal_credit(self):
        assert AccountType.LIABILITY.normal_balance == NormalBalance.CREDIT
        assert AccountType.EQUITY.normal_balance == NormalBalance.CREDIT
        assert AccountType.REVENUE.normal_balance == NormalBalance.CREDIT


class TestJournalLineValidation:
    def test_balanced_lines_pass(self):
        lines = [
            (Decimal("100.00"), Decimal("0.00"), "USD"),
            (Decimal("0.00"), Decimal("100.00"), "USD"),
        ]
        debits, credits = validate_journal_lines(lines, expected_currency="USD")
        assert debits == Decimal("100.00")
        assert credits == Decimal("100.00")

    def test_requires_at_least_two_lines(self):
        lines = [(Decimal("100.00"), Decimal("0.00"), "USD")]
        with pytest.raises(InvalidJournalLineError, match="requires at least two"):
            validate_journal_lines(lines)

    def test_rejects_negative_amounts(self):
        lines = [
            (Decimal("-50.00"), Decimal("0.00"), "USD"),
            (Decimal("0.00"), Decimal("-50.00"), "USD"),
        ]
        with pytest.raises(InvalidJournalLineError, match="cannot be negative"):
            validate_journal_lines(lines)

    def test_rejects_both_debit_and_credit_on_same_line(self):
        lines = [
            (Decimal("10.00"), Decimal("10.00"), "USD"),
            (Decimal("0.00"), Decimal("10.00"), "USD"),
        ]
        with pytest.raises(InvalidJournalLineError, match="exactly one"):
            validate_journal_lines(lines)

    def test_rejects_currency_mismatch(self):
        lines = [
            (Decimal("100.00"), Decimal("0.00"), "USD"),
            (Decimal("0.00"), Decimal("100.00"), "EUR"),
        ]
        with pytest.raises(CurrencyMismatchError, match="does not match journal currency"):
            validate_journal_lines(lines, expected_currency="USD")

    def test_rejects_unbalanced_lines(self):
        lines = [
            (Decimal("100.00"), Decimal("0.00"), "USD"),
            (Decimal("0.00"), Decimal("90.00"), "USD"),
        ]
        with pytest.raises(UnbalancedJournalEntryError, match="unbalanced"):
            validate_journal_lines(lines)


class TestPostingAndReversalValidation:
    def test_can_post_draft_balanced_entry(self):
        validate_can_post_entry(
            current_status=JournalEntryStatus.DRAFT,
            total_debits=Decimal("500.00"),
            total_credits=Decimal("500.00"),
        )

    def test_cannot_post_already_posted_or_reversed(self):
        with pytest.raises(ImmutableJournalEntryError, match="Only draft journal entries can be posted"):
            validate_can_post_entry(
                current_status=JournalEntryStatus.POSTED,
                total_debits=Decimal("100.00"),
                total_credits=Decimal("100.00"),
            )

    def test_cannot_post_unbalanced_entry(self):
        with pytest.raises(UnbalancedJournalEntryError):
            validate_can_post_entry(
                current_status=JournalEntryStatus.DRAFT,
                total_debits=Decimal("100.00"),
                total_credits=Decimal("150.00"),
            )

    def test_can_reverse_posted_entry(self):
        validate_can_reverse_entry(
            current_status=JournalEntryStatus.POSTED,
            is_already_reversed=False,
        )

    def test_cannot_reverse_draft_entry(self):
        with pytest.raises(ImmutableJournalEntryError, match="Only posted journal entries can be reversed"):
            validate_can_reverse_entry(
                current_status=JournalEntryStatus.DRAFT,
                is_already_reversed=False,
            )

    def test_cannot_reverse_already_reversed_entry(self):
        with pytest.raises(ImmutableJournalEntryError, match="already been reversed"):
            validate_can_reverse_entry(
                current_status=JournalEntryStatus.POSTED,
                is_already_reversed=True,
            )
