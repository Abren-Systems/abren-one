# Financial Architecture (Future Reference)

> **Status:** Principles locked. Implementation deferred until Finance is the active workstream.
> No empty ledger models or speculative abstractions will be created until then.

## Non-Negotiable Principles

1. Monetary values: `DecimalField` — never `FloatField`
2. Explicit currency on every financial record
3. Posted journal entries: balanced and immutable
4. Corrections: reversal/adjustment entries, not silent rewrites
5. Traceability: every financial transaction links to its originating business event
6. Funding restrictions and budget controls are financial concepts, not labels
7. Financial state transitions require authorization and produce audit events
8. Concurrency protection for contested financial operations (`select_for_update`)
9. The posted accounting records are the **authoritative financial source of truth**. Derived reporting projections and materialized aggregates are permitted for performance, provided they are traceable, reconcilable, and reproducible from the authoritative records
