# Finance Module

## Overview

The Finance module provides core double-entry bookkeeping, general ledger, chart of accounts management, balanced journal entries, and financial controls for organizations operating within Abren One.

## Principles

1. **Double-Entry Bookkeeping**: Every transaction is recorded through balanced debit and credit journal entry lines (`sum(debits) == sum(credits)`).
2. **Immutability of Posted Records**: Once a journal entry is posted, it cannot be edited or deleted. Corrections are performed via reversal and adjusting entries.
3. **Multi-Currency Support with Explicit Precision**: Every account and transaction uses explicit ISO 4217 currency codes and exact `Decimal` precision (never floating-point).
4. **Auditability & Traceability**: Every state transition (drafting, posting, reversing) generates an audit event with actor identity and correlation tracking.

## Components

- **Chart of Accounts (`Account`)**: Structured classification of financial accounts (`ASSET`, `LIABILITY`, `EQUITY`, `REVENUE`, `EXPENSE`).
- **Journal Entries (`JournalEntry`)**: Transaction headers tracking date, memo, status (`DRAFT`, `POSTED`, `REVERSED`), posting metadata, and reversal links.
- **Journal Lines (`JournalLine`)**: Granular debit and credit legs attached to a journal entry with database check constraints preventing simultaneous debit and credit on the same line.
- **Trial Balance (`get_trial_balance`)**: Authoritative aggregation of all posted debit and credit balances verifying overall ledger equilibrium.

## Public Interface (`public.py`)

- `AccountDTO`, `JournalEntryDTO`, `JournalLineDTO`, `TrialBalanceItemDTO`, `TrialBalanceDTO`
- Queries: `get_account_public`, `list_accounts_public`, `get_journal_entry_public`, `get_trial_balance_public`
- Commands: `create_account_public`, `create_journal_entry_public`, `post_journal_entry_public`, `reverse_journal_entry_public`
