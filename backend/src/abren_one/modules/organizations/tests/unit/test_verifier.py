import uuid

import pytest
from django.contrib.auth import get_user_model

from abren_one.modules.organizations.domain.value_objects import (
    MembershipRole,
    MembershipStatus,
    OrganizationStatus,
)
from abren_one.modules.organizations.infrastructure.verifier import (
    OrganizationMembershipVerifier,
)
from abren_one.modules.organizations.models import Membership, Organization
from abren_one.platform.tenancy.verifier import (
    get_membership_verifier,
    verify_user_membership,
)

User = get_user_model()


@pytest.mark.django_db
class TestOrganizationMembershipVerifier:
    def test_get_membership_returns_none_when_not_found(self) -> None:
        verifier = OrganizationMembershipVerifier()
        result = verifier.get_membership(user_id=uuid.uuid4(), organization_id=uuid.uuid4())
        assert result is None

    def test_get_membership_returns_info_when_found(self) -> None:
        user = User.objects.create_user(username="verifier_user", password="password")
        org = Organization.objects.create(name="Verifier Org", slug="verifier-org", status=OrganizationStatus.ACTIVE)
        Membership.objects.create(
            organization=org,
            user=user,
            role=MembershipRole.ADMIN.value,
            status=MembershipStatus.ACTIVE.value,
        )

        verifier = OrganizationMembershipVerifier()
        result = verifier.get_membership(user_id=user.id, organization_id=org.id)

        assert result is not None
        assert result.organization_id == org.id
        assert result.user_id == user.id
        assert result.role == "admin"
        assert result.status == "active"
        assert result.is_active is True

    def test_verify_user_membership_via_platform_registry(self) -> None:
        user = User.objects.create_user(username="registry_user", password="password")
        org = Organization.objects.create(name="Registry Org", slug="registry-org", status=OrganizationStatus.ACTIVE)
        Membership.objects.create(
            organization=org,
            user=user,
            role=MembershipRole.OWNER.value,
            status=MembershipStatus.ACTIVE.value,
        )

        assert get_membership_verifier() is not None
        result = verify_user_membership(user_id=user.id, organization_id=org.id)
        assert result is not None
        assert result.role == "owner"
        assert result.is_active is True
