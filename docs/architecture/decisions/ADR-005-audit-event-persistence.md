# ADR-005: Audit Event Persistence & Transaction Isolation

**Status:** Accepted
**Date:** 2026-11-15

## Context

Architecture Contracts §8.4 distinguishes between:
1. **Committed business audit events**: Recorded atomically with the business state mutation (same transaction).
2. **Security & access denial events**: Must be persisted independently, even if a business transaction or command rolls back.

In Django, wrapping persistence in `transaction.atomic(durable=True)` raises `RuntimeError: A durable atomic block cannot be nested within another atomic block` when called inside an outer `@transaction.atomic` block (which all business commands use). Furthermore, on a single database connection without autonomous transactions, savepoints within an outer transaction are inevitably rolled back if the outer transaction rolls back.

## Decision

1. **`record_audit_event`** continues to run inside the active business transaction, committing atomically with the operation.
2. **`record_security_event`** checks `connection.in_atomic_block`:
   - If called outside an atomic block (e.g., from middleware, DRF permission checks, or HTTP view exception handlers), it uses `transaction.atomic(durable=True)` to ensure immediate durable commit.
   - If called inside an existing atomic block, it executes within the current transaction block to avoid raising `RuntimeError`.
3. For true rollback-surviving independent persistence across all potential future scenarios, the architecture will introduce either:
   - A secondary database connection (`DATABASES["audit"]`), or
   - An asynchronous message queue / logging transport (e.g. out-of-band audit worker).
   This is deferred until the dedicated event streaming / logging platform stage.

## Consequences

- Security events recorded at the request boundary (middleware, permissions) commit durably and immediately.
- Commands or tests can invoke `record_security_event` without encountering a `RuntimeError`.
- Clear roadmap established for secondary database / out-of-band audit trail routing.
