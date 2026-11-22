"""Exceptions for the Finance domain."""

from __future__ import annotations

from abren_one.platform.common.exceptions import DomainError, NotFoundError


class FinanceDomainError(DomainError):
    """Base exception for domain errors in Finance."""


class UnbalancedJournalEntryError(FinanceDomainError):
    """Raised when a journal entry's debits do not equal its credits."""


class ImmutableJournalEntryError(FinanceDomainError):
    """Raised when attempting to modify or delete a posted or reversed journal entry."""


class InvalidJournalLineError(FinanceDomainError):
    """Raised when a journal line has invalid debit/credit configuration."""


class InvalidAccountTypeError(FinanceDomainError):
    """Raised when an invalid account type is specified."""


class CurrencyMismatchError(FinanceDomainError):
    """Raised when journal lines or accounts have incompatible currencies."""


class AccountNotFoundError(NotFoundError, FinanceDomainError):
    """Raised when an account is not found in the current organization."""


class JournalEntryNotFoundError(NotFoundError, FinanceDomainError):
    """Raised when a journal entry is not found in the current organization."""
