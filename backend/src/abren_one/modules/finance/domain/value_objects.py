"""Value objects and enumerations for the Finance domain."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class AccountType(StrEnum):
    """Primary account classifications per standard double-entry bookkeeping."""

    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

    @property
    def normal_balance(self) -> NormalBalance:
        if self in (AccountType.ASSET, AccountType.EXPENSE):
            return NormalBalance.DEBIT
        return NormalBalance.CREDIT


class NormalBalance(StrEnum):
    """The normal balance expectation for an account."""

    DEBIT = "debit"
    CREDIT = "credit"


class JournalEntryStatus(StrEnum):
    """Lifecycle states of a journal entry."""

    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"


@dataclass(frozen=True)
class Money:
    """Represents an explicit monetary amount and ISO 4217 currency."""

    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        if len(self.currency) != 3 or not self.currency.isupper():
            raise ValueError(f"Invalid currency code: {self.currency}")
