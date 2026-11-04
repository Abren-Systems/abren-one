# Transaction Model and Conventions

**Applies to:** All modules in the Abren One backend
**Source of truth:** Architecture Contracts §6.4, §8.4, Appendix B

---

## Overview

Abren One uses **explicit, per-command transaction boundaries**. The global `ATOMIC_REQUESTS` setting is **not** used. Every state-changing operation declares its own transaction scope via `@transaction.atomic`.

This document defines the conventions for transaction management, concurrency control, and audit event persistence.

---

## Command Transactions

Every state-changing command is wrapped in `@transaction.atomic`:

```python
from django.db import transaction
from abren_one.platform.common.context import ExecutionContext


@transaction.atomic
def execute(data: CreateOrganizationInput) -> CreateOrganizationResult:
    """
    All model writes within this function are committed
    together or rolled back together.
    """
    # 1. Validate business rules
    # 2. Persist state changes
    # 3. Record audit event (committed atomically)
    # 4. Return result DTO
    ...
```

**Rules:**

- One `@transaction.atomic` per command — this is the operation boundary.
- The decorator goes on the `execute` function, not on internal helpers.
- All model creates, updates, and deletes within the command participate in the same transaction.
- If any step raises an exception, the entire transaction is rolled back.

---

## Query Transactions

Read-only queries do **not** need a transaction decorator:

```python
def execute(*, organization_id: UUID) -> GetOrganizationResult:
    """No @transaction.atomic needed — this is read-only."""
    org = Organization.objects.get(id=organization_id)
    return GetOrganizationResult(
        id=org.id,
        name=org.name,
        slug=org.slug,
        is_active=org.is_active,
    )
```

**Rules:**

- Queries must not perform state changes.
- Django's default `AUTOCOMMIT` mode handles read consistency.
- If a query needs snapshot isolation across multiple reads, use `@transaction.atomic` with an explicit justification comment.

---

## Multi-Model Operations

When a single command modifies multiple models, the command's `@transaction.atomic` wraps all writes:

```python
@transaction.atomic
def execute(data: InviteMemberInput) -> InviteMemberResult:
    """
    Creates a Membership record AND records an audit event —
    both committed atomically.
    """
    membership = Membership.objects.create(
        organization_id=data.context.organization_id,
        user_id=data.user_id,
        status=MembershipStatus.INVITED,
    )
    
    # Audit event committed in the same transaction
    record_audit_event(
        context=data.context,
        action="membership.invited",
        target_type="organizations.Membership",
        target_id=membership.id,
        outcome="success",
    )
    
    return InviteMemberResult(membership_id=membership.id)
```

There is no need for nested transactions or separate transaction blocks for related writes within a single command.

---

## Cross-Module State Changes

When a command in module A calls a published command in module B's `public.py`, the calling command's transaction wraps the entire operation:

```python
# In module A
@transaction.atomic
def execute(data: SomeComplexInput) -> SomeComplexResult:
    # 1. Local state change in module A
    local_record = MyModel.objects.create(...)

    # 2. Cross-module command call (via public.py)
    #    This participates in the SAME transaction
    from abren_one.modules.other_module.public import some_command

    other_result = some_command.execute(other_input)

    # 3. More local state changes
    #    If anything above fails, EVERYTHING rolls back
    ...
```

**Rules:**

- The outer command owns the transaction boundary.
- The called command's `@transaction.atomic` creates a **savepoint** (Django's nested atomic behavior).
- If the inner command fails, only its savepoint is rolled back — the outer command can catch the exception and decide whether to proceed or propagate the failure.
- If the outer command fails, everything (including the inner command's writes) is rolled back.

---

## Nested `@transaction.atomic` — Savepoints

Django's `@transaction.atomic` creates savepoints when nested:

```python
@transaction.atomic  # Opens transaction
def outer_command():
    Model.objects.create(...)  # Write 1

    try:

        @transaction.atomic  # Creates SAVEPOINT
        def inner_operation():
            Model.objects.create(...)  # Write 2
            raise SomeError()  # Rolls back to SAVEPOINT

        inner_operation()
    except SomeError:
        pass  # Write 1 is preserved

    Model.objects.create(...)  # Write 3
    # COMMIT: Write 1 and Write 3 are committed; Write 2 was rolled back
```

Use this pattern when partial failure within a larger operation is acceptable and the outer command can recover.

---

## Concurrent Access

### `select_for_update()` — Pessimistic Locking

Use `select_for_update()` on contested records to prevent lost updates:

```python
@transaction.atomic
def execute(data: UpdateBalanceInput) -> UpdateBalanceResult:
    # Lock the record for the duration of this transaction
    account = Account.objects.select_for_update().get(
        id=data.account_id,
        organization_id=data.context.organization_id,
    )
    
    # Safe to read-modify-write — no other transaction can modify this row
    account.balance += data.amount
    account.save()
    ...
```

**When to use `select_for_update()`:**

| Scenario | Required? |
|----------|-----------|
| Financial / inventory records | **Yes** — mandatory |
| Membership status transitions | Recommended |
| Counter / sequence updates | Yes |
| Regular CRUD (no contention expected) | No |

### Optimistic Concurrency — Version Fields

For records where pessimistic locking is too expensive or not appropriate, use a version field:

```python
@transaction.atomic
def execute(data: UpdateRecordInput) -> UpdateRecordResult:
    updated_count = MyModel.objects.filter(
        id=data.record_id,
        version=data.expected_version,  # Check version at write time
    ).update(
        field=data.new_value,
        version=F("version") + 1,
    )

    if updated_count == 0:
        raise ConcurrentModificationError("Record was modified by another operation")
```

**Rules:**

- The version field is checked at write time, not read time.
- A mismatch means another operation modified the record — the command raises an error.
- The caller decides whether to retry or report the conflict.

---

## Audit Event Persistence

Audit events have **different transaction behavior** depending on the outcome:

### Successful Operations

Audit events for successful operations are committed **atomically** within the same transaction as the business state change:

```python
@transaction.atomic
def execute(data: ApproveGrantInput) -> ApproveGrantResult:
    grant = Grant.objects.select_for_update().get(id=data.grant_id)
    grant.status = GrantStatus.APPROVED
    grant.save()
    
    # Audit event committed WITH the business change
    record_audit_event(
        context=data.context,
        action="grant.approved",
        target_type="programs.Grant",
        target_id=grant.id,
        outcome="success",
        metadata={"previous_status": "pending"},
    )
    
    return ApproveGrantResult(grant_id=grant.id)
```

If the transaction rolls back, the audit event rolls back too — which is correct, because the business change didn't happen.

### Denied / Failed Attempts

Audit events for denied or failed security-relevant attempts must **survive transaction rollback**. These are persisted through an independently committed path:

```python
@transaction.atomic
def execute(data: ApproveGrantInput) -> ApproveGrantResult:
    try:
        # Authorization check
        if not is_authorized(data.context, "grant.approve"):
            # This audit event must survive even if the transaction rolls back
            record_security_event(  # Uses independent DB connection or deferred write
                context=data.context,
                action="grant.approve",
                target_type="programs.Grant",
                target_id=data.grant_id,
                outcome="denied",
                metadata={"reason": "insufficient_permissions"},
            )
            raise PermissionDenied("Not authorized to approve grants")
        
        # ... proceed with business logic
    except BusinessRuleViolation as e:
        record_security_event(
            context=data.context,
            action="grant.approve",
            outcome="failed",
            metadata={"reason": str(e)},
        )
        raise
```

### What About `transaction.on_commit`?

`transaction.on_commit` runs a callback **only after the transaction successfully commits**. It is discarded on rollback.

| Use Case | `transaction.on_commit` Appropriate? |
|----------|--------------------------------------|
| Sending a notification email after success | ✅ Yes |
| Triggering a background job after success | ✅ Yes |
| Persisting a denied-access audit event | ❌ No — would be lost on rollback |
| Recording a failed business rule check | ❌ No — would be lost on rollback |

```python
@transaction.atomic
def execute(data: InviteMemberInput) -> InviteMemberResult:
    membership = Membership.objects.create(...)

    # Notification sent ONLY after successful commit
    transaction.on_commit(lambda: send_invitation_email.delay(membership.id))

    return InviteMemberResult(membership_id=membership.id)
```

---

## Django Configuration

### `ATOMIC_REQUESTS` Is NOT Used

```python
# settings/base.py
DATABASES = {
    "default": {
        # ...
        # ATOMIC_REQUESTS is NOT set (defaults to False)
    }
}
```

**Rationale:** Wrapping every HTTP request in a transaction:
- Obscures which operations are actually state-changing.
- Makes it harder to reason about transaction boundaries.
- Prevents fine-grained control over what commits together.
- Complicates audit event persistence for denied attempts.

Instead, each command explicitly declares its transaction scope.

### Long-Running Transactions

Avoid holding transactions open for extended periods:

- Do not perform external API calls inside `@transaction.atomic`.
- Do not perform file I/O inside `@transaction.atomic`.
- Do not wait for user input inside `@transaction.atomic`.
- Keep the critical section (the `@transaction.atomic` block) as small as possible.

If a command must call an external service, structure it so the external call happens **outside** the transaction:

```python
def execute(data: SomeInput) -> SomeResult:
    # 1. External call (outside transaction)
    external_result = call_external_api(data.external_id)
    
    # 2. State change (inside transaction)
    with transaction.atomic():
        record = MyModel.objects.create(
            external_ref=external_result.ref,
            ...
        )
        record_audit_event(...)
    
    return SomeResult(record_id=record.id)
```

---

## Financial Transactions (Future — When Finance Module Is Implemented)

These conventions are documented now and enforced when the Finance module is the active workstream:

| Convention | Rule |
|------------|------|
| Journal entries | Balanced and immutable — once posted, they cannot be modified |
| Corrections | Use reversal entries, not rewrites of existing records |
| Monetary values | `DecimalField` — never `FloatField` |
| Currency | Explicit currency field on every financial record |
| Concurrency | `select_for_update()` mandatory for contested financial records |
| Audit | Every financial state transition produces an audit event |
| Traceability | Every financial transaction links to its originating business event |

```python
# Future pattern — DO NOT implement until Finance module begins
@transaction.atomic
def execute(data: PostJournalEntryInput) -> PostJournalEntryResult:
    # Lock the accounts involved
    accounts = Account.objects.select_for_update().filter(
        id__in=[data.debit_account_id, data.credit_account_id],
        organization_id=data.context.organization_id,
    )
    
    # Validate the entry balances (debits == credits)
    # Create immutable journal entry
    # Update account balances
    # Record audit event
    ...
```

---

## Summary Table

| Scenario | Convention |
|----------|-----------|
| State-changing command | `@transaction.atomic` on the `execute` function |
| Read-only query | No transaction decorator |
| Multi-model writes in one command | Single `@transaction.atomic` on the command |
| Cross-module state change | Calling command's transaction wraps everything |
| Nested `@transaction.atomic` | Creates savepoints |
| Contested records (financial/inventory) | `select_for_update()` |
| Optimistic concurrency | Version field checked at write time |
| Successful audit event | Committed atomically within the same transaction |
| Denied/failed audit event | Persisted independently (survives rollback) |
| Post-commit side effects | `transaction.on_commit` for notifications only |
| Global `ATOMIC_REQUESTS` | **Not used** — transactions are explicit per command |
| Long-running transactions | Avoided — keep external calls outside the atomic block |
| Financial records (future) | Immutable journal entries, reversal corrections, `select_for_update()` mandatory |
