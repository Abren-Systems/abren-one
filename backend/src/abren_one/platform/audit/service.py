from __future__ import annotations

from typing import Any
from uuid import UUID

from django.db import transaction

from abren_one.platform.audit.models import AuditEvent


def record_audit_event(
    *,
    actor_type: str,
    actor_id: UUID | None,
    organization_id: UUID | None,
    action: str,
    target_type: str,
    target_id: UUID,
    correlation_id: UUID,
    outcome: str = "success",
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    """Record a business audit event committed atomically with the operation (§8.4).

    Used for successful business operations.
    """
    return AuditEvent.objects.create(
        actor_type=actor_type,
        actor_id=actor_id,
        organization_id=organization_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        correlation_id=correlation_id,
        outcome=outcome,
        metadata=metadata or {},
    )


def record_security_event(
    *,
    actor_type: str,
    actor_id: UUID | None,
    organization_id: UUID | None,
    action: str,
    target_type: str,
    target_id: UUID,
    correlation_id: UUID,
    outcome: str = "denied",
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    """Record a denied or failed security event independently (§8.4).

    Must be committed independently so that if a business transaction
    rolls back, this security/audit record survives.
    """
    with transaction.atomic(durable=True):
        return AuditEvent.objects.create(
            actor_type=actor_type,
            actor_id=actor_id,
            organization_id=organization_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            correlation_id=correlation_id,
            outcome=outcome,
            metadata=metadata or {},
        )
