import uuid

import pytest
from django.contrib.auth import get_user_model

from abren_one.modules.organizations.application.commands.activate_membership import (
    ActivateMembershipInput,
)
from abren_one.modules.organizations.application.commands.activate_membership import (
    execute as activate_membership,
)
from abren_one.modules.organizations.application.commands.add_member import (
    AddMemberInput,
)
from abren_one.modules.organizations.application.commands.add_member import (
    execute as add_member,
)
from abren_one.modules.organizations.application.commands.create_branch import (
    CreateBranchInput,
)
from abren_one.modules.organizations.application.commands.create_branch import (
    execute as create_branch,
)
from abren_one.modules.organizations.application.commands.create_organization import (
    CreateOrganizationInput,
)
from abren_one.modules.organizations.application.commands.create_organization import (
    execute as create_organization,
)
from abren_one.modules.organizations.application.commands.revoke_membership import (
    RevokeMembershipInput,
)
from abren_one.modules.organizations.application.commands.revoke_membership import (
    execute as revoke_membership,
)
from abren_one.modules.organizations.application.commands.suspend_membership import (
    SuspendMembershipInput,
)
from abren_one.modules.organizations.application.commands.suspend_membership import (
    execute as suspend_membership,
)
from abren_one.modules.organizations.application.queries.get_organization import (
    execute as get_organization,
)
from abren_one.modules.organizations.application.queries.list_branches import (
    execute as list_branches,
)
from abren_one.modules.organizations.application.queries.list_members import (
    execute as list_members,
)
from abren_one.modules.organizations.domain.exceptions import (
    CannotRevokeLastOwnerError,
    DuplicateMembershipError,
    OrganizationError,
)
from abren_one.modules.organizations.domain.value_objects import (
    MembershipRole,
    MembershipStatus,
)
from abren_one.platform.audit.models import AuditEvent
from abren_one.platform.common.context import ActorType, ExecutionContext

User = get_user_model()


@pytest.mark.django_db
class TestOrganizationCommandsAndQueries:
    def test_create_organization_provisions_owner_and_audit(self) -> None:
        user = User.objects.create_user(username="founder", password="password123")
        correlation_id = uuid.uuid4()
        context = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=user.id,
            organization_id=None,
            correlation_id=correlation_id,
        )

        result = create_organization(
            CreateOrganizationInput(
                context=context,
                name="Hope Foundation",
                slug="hope-foundation",
            )
        )

        org_details = get_organization(organization_id=result.organization_id)
        assert org_details.name == "Hope Foundation"
        assert org_details.slug == "hope-foundation"
        assert org_details.is_active is True

        members = list_members(organization_id=result.organization_id)
        assert len(members) == 1
        assert members[0].user_id == user.id
        assert members[0].role == MembershipRole.OWNER.value
        assert members[0].status == MembershipStatus.ACTIVE.value

        # Verify audit trail
        audit_events = AuditEvent.objects.filter(target_id=result.organization_id)
        assert audit_events.exists()
        assert audit_events.first().action == "organization.created"

    def test_duplicate_organization_slug_fails(self) -> None:
        user = User.objects.create_user(username="founder2", password="password123")
        context = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=user.id,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )

        create_organization(CreateOrganizationInput(context=context, name="Org 1", slug="duplicate-slug"))
        with pytest.raises(OrganizationError, match="already exists"):
            create_organization(CreateOrganizationInput(context=context, name="Org 2", slug="duplicate-slug"))

    def test_create_branch_in_organization(self) -> None:
        user = User.objects.create_user(username="founder3", password="password123")
        ctx_provision = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=user.id,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org = create_organization(CreateOrganizationInput(context=ctx_provision, name="Org", slug="branch-org"))

        ctx_tenant = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=user.id,
            organization_id=org.organization_id,
            correlation_id=uuid.uuid4(),
        )
        branch_result = create_branch(
            CreateBranchInput(
                context=ctx_tenant,
                name="Regional Office",
                code="RO-1",
                is_headquarters=True,
            )
        )

        branches = list_branches(organization_id=org.organization_id)
        assert len(branches) == 1
        assert branches[0].id == branch_result.branch_id
        assert branches[0].code == "RO-1"
        assert branches[0].is_headquarters is True

    def test_membership_lifecycle(self) -> None:
        owner = User.objects.create_user(username="owner", password="password123")
        member = User.objects.create_user(username="member", password="password123")

        ctx_provision = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=owner.id,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org = create_organization(CreateOrganizationInput(context=ctx_provision, name="Lifecycle Org", slug="life-org"))

        ctx_tenant = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=owner.id,
            organization_id=org.organization_id,
            correlation_id=uuid.uuid4(),
        )

        # 1. Add member
        add_result = add_member(
            AddMemberInput(
                context=ctx_tenant,
                user_id=member.id,
                role=MembershipRole.STAFF.value,
            )
        )
        membership_id = add_result.membership_id

        # Duplicate fails
        with pytest.raises(DuplicateMembershipError):
            add_member(AddMemberInput(context=ctx_tenant, user_id=member.id))

        # 2. Suspend member
        suspend_result = suspend_membership(SuspendMembershipInput(context=ctx_tenant, membership_id=membership_id))
        assert suspend_result.status == MembershipStatus.SUSPENDED.value

        # 3. Activate member
        act_result = activate_membership(ActivateMembershipInput(context=ctx_tenant, membership_id=membership_id))
        assert act_result.status == MembershipStatus.ACTIVE.value

        # 4. Revoke member
        revoke_result = revoke_membership(RevokeMembershipInput(context=ctx_tenant, membership_id=membership_id))
        assert revoke_result.membership_id == membership_id

    def test_cannot_revoke_last_owner(self) -> None:
        owner = User.objects.create_user(username="sole_owner", password="password123")
        ctx_provision = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=owner.id,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org = create_organization(CreateOrganizationInput(context=ctx_provision, name="Owner Org", slug="owner-org"))

        members = list_members(organization_id=org.organization_id)
        owner_membership_id = members[0].membership_id

        ctx_tenant = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=owner.id,
            organization_id=org.organization_id,
            correlation_id=uuid.uuid4(),
        )

        with pytest.raises(CannotRevokeLastOwnerError, match="Cannot revoke the last active owner"):
            revoke_membership(
                RevokeMembershipInput(
                    context=ctx_tenant,
                    membership_id=owner_membership_id,
                )
            )
