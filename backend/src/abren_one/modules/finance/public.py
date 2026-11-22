"""Public interface for the Finance module (§3.1, §3.4).

Other modules must import ONLY from this file.
"""

from abren_one.modules.finance.application.commands.create_account import (
    CreateAccountInput,
    CreateAccountResult,
)
from abren_one.modules.finance.application.commands.create_account import (
    execute as create_account,
)
from abren_one.modules.finance.application.commands.create_journal_entry import (
    CreateJournalEntryInput,
    CreateJournalEntryResult,
    JournalLineInput,
)
from abren_one.modules.finance.application.commands.create_journal_entry import (
    execute as create_journal_entry,
)
from abren_one.modules.finance.application.commands.post_journal_entry import (
    PostJournalEntryInput,
    PostJournalEntryResult,
)
from abren_one.modules.finance.application.commands.post_journal_entry import (
    execute as post_journal_entry,
)
from abren_one.modules.finance.application.commands.reverse_journal_entry import (
    ReverseJournalEntryInput,
    ReverseJournalEntryResult,
)
from abren_one.modules.finance.application.commands.reverse_journal_entry import (
    execute as reverse_journal_entry,
)
from abren_one.modules.finance.application.exceptions import (
    AccountNotFoundError,
    CurrencyMismatchError,
    FinanceDomainError,
    ImmutableJournalEntryError,
    InvalidAccountTypeError,
    InvalidJournalLineError,
    JournalEntryNotFoundError,
    UnbalancedJournalEntryError,
)
from abren_one.modules.finance.application.queries.get_account import (
    AccountDetailResult,
)
from abren_one.modules.finance.application.queries.get_account import (
    execute as get_account,
)
from abren_one.modules.finance.application.queries.get_journal_entry import (
    JournalEntryDetailResult,
    JournalLineDetailResult,
)
from abren_one.modules.finance.application.queries.get_journal_entry import (
    execute as get_journal_entry,
)
from abren_one.modules.finance.application.queries.get_trial_balance import (
    TrialBalanceItem,
    TrialBalanceResult,
)
from abren_one.modules.finance.application.queries.get_trial_balance import (
    execute as get_trial_balance,
)
from abren_one.modules.finance.application.queries.list_accounts import (
    AccountSummaryResult,
)
from abren_one.modules.finance.application.queries.list_accounts import (
    execute as list_accounts,
)
from abren_one.modules.finance.application.queries.list_journal_entries import (
    JournalEntrySummaryResult,
)
from abren_one.modules.finance.application.queries.list_journal_entries import (
    execute as list_journal_entries,
)
from abren_one.modules.finance.domain.value_objects import (
    AccountType,
    JournalEntryStatus,
    Money,
    NormalBalance,
)

__all__ = [
    # Enums & Value Objects
    "AccountType",
    "JournalEntryStatus",
    "Money",
    "NormalBalance",
    # DTOs
    "CreateAccountInput",
    "CreateAccountResult",
    "JournalLineInput",
    "CreateJournalEntryInput",
    "CreateJournalEntryResult",
    "PostJournalEntryInput",
    "PostJournalEntryResult",
    "ReverseJournalEntryInput",
    "ReverseJournalEntryResult",
    "AccountDetailResult",
    "AccountSummaryResult",
    "JournalEntryDetailResult",
    "JournalLineDetailResult",
    "JournalEntrySummaryResult",
    "TrialBalanceItem",
    "TrialBalanceResult",
    # Commands
    "create_account",
    "create_journal_entry",
    "post_journal_entry",
    "reverse_journal_entry",
    # Queries
    "get_account",
    "list_accounts",
    "get_journal_entry",
    "list_journal_entries",
    "get_trial_balance",
    # Exceptions
    "FinanceDomainError",
    "AccountNotFoundError",
    "JournalEntryNotFoundError",
    "UnbalancedJournalEntryError",
    "ImmutableJournalEntryError",
    "InvalidJournalLineError",
    "InvalidAccountTypeError",
    "CurrencyMismatchError",
]
