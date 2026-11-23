# ADR-006: Cross-Module Operational Bridges

## Status

Accepted

## Context

Abren One's modular monolith has seven business modules operating with strong
boundary enforcement (AST Rule 3, `public.py` contracts, import-linter).
Each module handles its domain transactions independently.

However, real humanitarian operations require operational continuity across
modules:

- When a **Goods Receipt** is intaked into inventory, the finance team expects
  an automatic journal entry debiting Inventory Asset and crediting AP Clearing.
- When inventory is **issued for program delivery**, it should generate a
  journal entry debiting Program Relief Expenditure and crediting Inventory Asset.
- When stock is **written off** (damage, expiry, loss), a loss entry should post
  to the General Ledger.
- When an **in-kind donation** is received into inventory, its fair value should
  be journalized.
- When a **monetary donation** is recorded in fundraising, the GL should reflect
  the cash receipt and revenue recognition.

Without these bridges, finance teams must manually create journal entries for
every operational event — the exact problem Abren One was designed to solve.

## Decision

### Bridge Pattern: Application-Layer Services

Each cross-module integration is implemented as an **application-layer bridge
service** that:

1. Lives inside the **triggering module's** `application/bridges/` directory.
2. Imports only from the **target module's** `public.py` (never internal models).
3. Is called by the triggering command **after** the primary domain operation
   succeeds, within the same `@transaction.atomic` boundary.
4. Uses a **SYSTEM actor context** for the GL posting to separate the financial
   recording responsibility from the operational actor.

### Standard Account Codes

Bridges resolve GL accounts by **code** (not UUID) using a new
`get_account_by_code` query on `finance.public`. This ensures that any
organization with a properly seeded Chart of Accounts will have automatic
GL integration.

Standard account codes used by bridges:

| Code | Name | Type | Used By |
|------|------|------|---------|
| 1200 | Inventory Asset | Asset | Stock receipt, issue, write-off |
| 2010 | Accounts Payable – Goods Clearing | Liability | Purchase receipt |
| 5100 | Program Relief Expenditure | Expense | Program stock issue |
| 5800 | Inventory Shrinkage / Loss | Expense | Write-off |
| 1010 | Cash / Bank | Asset | Monetary donations |
| 3100 | Donor Revenue – Temporarily Restricted | Revenue | Monetary donations |
| 3200 | In-Kind Donation Revenue | Revenue | In-kind donations |
| 5000 | General Operational Expenditure | Expense | General stock issue |

### Failure Strategy

If a GL account code is not found in the organization's Chart of Accounts,
the bridge **logs a warning** and **does not raise** — the operational
transaction (e.g., stock receipt) succeeds, but no GL entry is created.
This is the "graceful degradation" approach: organizations that have not
yet set up their Chart of Accounts can still operate, while organizations
with a configured CoA get automatic financial integration.

### Why Not Django Signals or Domain Events?

- **Django signals** create hidden coupling and make transaction boundaries
  opaque. A developer reading `receive_purchased_stock.py` would not know
  that a GL entry is being created unless they grep for signal connections.
- **Domain events (async)** would break the transactional guarantee — the
  stock receipt could succeed while the GL entry fails silently.
- **Explicit bridge calls** are visible in the command code, run within the
  same transaction, and can be traced, tested, and disabled independently.

## Consequences

### Positive

- Zero-configuration financial integration for organizations with standard CoA.
- Full audit trail linking operational events to their GL postings.
- All cross-module imports remain through `public.py` — no architecture
  contract violations.
- Bridge calls are explicit and testable in isolation.

### Negative

- Slight coupling between operational commands and finance module. Acceptable
  because finance integration is a core value proposition of the platform.
- Each new operational event type requires a bridge function. Manageable because
  the humanitarian domain has a finite, well-known set of transaction types.

### Neutral

- Organizations without a configured Chart of Accounts experience no change.
- Bridges add ~10-20ms to transactional commands (one additional DB query for
  account lookup + one journal entry creation).
