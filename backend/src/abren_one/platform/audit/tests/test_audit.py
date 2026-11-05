import uuid

import pytest
from django.core.exceptions import PermissionDenied

from abren_one.platform.audit.service import record_audit_event, record_security_event


@pytest.mark.django_db
class TestAuditEventModel:
    def test_create_audit_event(self) -> None:
        event = record_audit_event(
            actor_type="user",
            actor_id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            action="organization.created",
            target_type="organizations.Organization",
            target_id=uuid.uuid4(),
            correlation_id=uuid.uuid4(),
            outcome="success",
            metadata={"source": "api"},
        )
        assert isinstance(event.id, uuid.UUID)
        assert event.action == "organization.created"
        assert event.outcome == "success"
        assert event.metadata == {"source": "api"}

    def test_audit_event_is_immutable_against_update(self) -> None:
        event = record_audit_event(
            actor_type="user",
            actor_id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            action="organization.created",
            target_type="organizations.Organization",
            target_id=uuid.uuid4(),
            correlation_id=uuid.uuid4(),
        )
        event.action = "tampered.action"
        with pytest.raises(PermissionDenied, match="immutable and cannot be updated"):
            event.save()

    def test_audit_event_is_immutable_against_delete(self) -> None:
        event = record_audit_event(
            actor_type="user",
            actor_id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            action="organization.created",
            target_type="organizations.Organization",
            target_id=uuid.uuid4(),
            correlation_id=uuid.uuid4(),
        )
        with pytest.raises(PermissionDenied, match="immutable and cannot be deleted"):
            event.delete()

    def test_record_security_event_denied(self) -> None:
        event = record_security_event(
            actor_type="user",
            actor_id=uuid.uuid4(),
            organization_id=uuid.uuid4(),
            action="organization.access_denied",
            target_type="organizations.Organization",
            target_id=uuid.uuid4(),
            correlation_id=uuid.uuid4(),
            outcome="denied",
            metadata={"reason": "membership_inactive"},
        )
        assert event.outcome == "denied"
        assert event.metadata["reason"] == "membership_inactive"
