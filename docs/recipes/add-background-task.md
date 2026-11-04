# Recipe: Add a Background Task

## Steps

### 1. Create the task file

Background tasks live in the module's `infrastructure/` directory:

```
backend/src/abren_one/modules/<module>/infrastructure/tasks.py
```

### 2. Define the task with explicit context

Tasks must carry an explicit `ExecutionContext` — they must not assume the caller's tenant context or rely on ambient state.

```python
import logging
from uuid import UUID

from abren_one.platform.common.context import ActorType, ExecutionContext

logger = logging.getLogger(__name__)


def send_membership_welcome_email(
    *,
    organization_id: UUID,
    membership_id: UUID,
    correlation_id: UUID,
) -> None:
    """
    Send a welcome email to a newly activated member.

    This task is idempotent — re-sending the same welcome email
    for an already-welcomed member is a no-op.
    """
    context = ExecutionContext(
        actor_type=ActorType.SYSTEM,
        actor_id=None,
        organization_id=organization_id,
        correlation_id=correlation_id,
    )

    try:
        # 1. Load membership within the given organization
        from abren_one.modules.organizations.models import Membership

        membership = Membership.objects.get(
            id=membership_id,
            organization_id=context.organization_id,
        )

        # 2. Guard: idempotency check
        if membership.welcome_email_sent:
            logger.info(
                "Welcome email already sent for membership %s, skipping.",
                membership_id,
            )
            return

        # 3. Perform the work
        # ... send the email ...

        # 4. Mark complete
        membership.welcome_email_sent = True
        membership.save(update_fields=["welcome_email_sent"])

        logger.info(
            "Welcome email sent for membership %s (correlation: %s).",
            membership_id,
            correlation_id,
        )

    except Membership.DoesNotExist:
        logger.error(
            "Membership %s not found in organization %s (correlation: %s).",
            membership_id,
            organization_id,
            correlation_id,
        )
        raise

    except Exception:
        logger.exception(
            "Failed to send welcome email for membership %s (correlation: %s).",
            membership_id,
            correlation_id,
        )
        raise
```

### 3. Call the task from a command

Tasks are triggered by application commands, typically after a successful state change:

```python
from django.db import transaction

from abren_one.modules.organizations.infrastructure.tasks import (
    send_membership_welcome_email,
)


@transaction.atomic
def execute(data: ActivateMembershipInput) -> ActivateMembershipResult:
    # ... activate membership ...

    # Schedule the task after the transaction commits
    transaction.on_commit(
        lambda: send_membership_welcome_email(
            organization_id=data.context.organization_id,
            membership_id=membership.id,
            correlation_id=data.context.correlation_id,
        )
    )

    return ActivateMembershipResult(membership_id=membership.id)
```

### 4. Write tests

```python
# modules/<module>/tests/integration/test_send_membership_welcome_email.py
```

Test that:

- The task completes successfully with valid inputs
- The task is idempotent (calling it twice produces no side effects)
- The task fails explicitly when the record doesn't exist
- The task respects organization boundaries

## Task Design Rules

### Explicit context — no ambient state

Every task receives all the context it needs via explicit parameters:

- `organization_id` — which tenant this task operates on
- A record identifier (e.g., `membership_id`)
- `correlation_id` — for tracing the operation back to its origin

Tasks must never reach into request-scoped or thread-local state.

### Actor type

- Use `ActorType.SYSTEM` for system-initiated tasks (scheduled jobs, post-commit hooks)
- Use `ActorType.INTEGRATION` for tasks triggered by external systems

### Idempotency

Tasks should be idempotent where possible. If a task is retried (due to a crash, timeout, or queue replay), re-execution should be safe:

- Check whether the work has already been done before doing it
- Use `update_fields` to limit writes
- Avoid side effects that can't be repeated safely

### Error handling

- Log failures with full context (`organization_id`, record ID, `correlation_id`)
- Do not silently swallow exceptions — let them propagate so the task runner can retry or report
- Use `logger.exception()` for unexpected errors to capture the traceback

### Transaction boundaries

- Tasks run outside the calling command's transaction
- Use `transaction.on_commit()` in the calling command to ensure the task only runs after the triggering state change is committed
- If the task itself needs a transaction, wrap its database operations explicitly

## Task Runner

> [!NOTE]
> The task runner (Celery, Django-Q, etc.) is a future decision. For now, write tasks as plain Python functions with explicit parameters. When a task runner is selected, these functions will be wrapped with the runner's decorator (e.g., `@shared_task`) with minimal changes.

## Rules

- Tasks live in `modules/<name>/infrastructure/tasks.py`
- Explicit `ExecutionContext` — no ambient tenant state
- Pass `organization_id`, record identifiers, and `correlation_id` as parameters
- Idempotent where possible
- Log failures, don't swallow exceptions
- Use `transaction.on_commit()` to schedule tasks after the calling command commits
- Task runner selection is deferred — write plain functions for now
