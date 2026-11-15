import pytest

from abren_one.modules.organizations.domain.policies import (
    can_revoke_membership,
    can_transition_membership_status,
    can_transition_org_status,
    is_membership_allowed_access,
)
from abren_one.modules.organizations.domain.value_objects import (
    MembershipRole,
    MembershipStatus,
    OrganizationStatus,
)


class TestOrganizationStatusTransitions:
    def test_provisioning_can_transition_to_active(self) -> None:
        assert can_transition_org_status(OrganizationStatus.PROVISIONING, OrganizationStatus.ACTIVE) is True

    def test_provisioning_can_transition_to_archived(self) -> None:
        assert can_transition_org_status(OrganizationStatus.PROVISIONING, OrganizationStatus.ARCHIVED) is True

    def test_active_can_transition_to_suspended(self) -> None:
        assert can_transition_org_status(OrganizationStatus.ACTIVE, OrganizationStatus.SUSPENDED) is True

    def test_suspended_can_transition_to_active(self) -> None:
        assert can_transition_org_status(OrganizationStatus.SUSPENDED, OrganizationStatus.ACTIVE) is True

    def test_archived_is_terminal(self) -> None:
        assert can_transition_org_status(OrganizationStatus.ARCHIVED, OrganizationStatus.ACTIVE) is False
        assert can_transition_org_status(OrganizationStatus.ARCHIVED, OrganizationStatus.SUSPENDED) is False

    def test_same_status_transition_is_noop(self) -> None:
        assert can_transition_org_status(OrganizationStatus.ACTIVE, OrganizationStatus.ACTIVE) is True


class TestMembershipStatusTransitions:
    def test_invited_to_active(self) -> None:
        assert can_transition_membership_status(MembershipStatus.INVITED, MembershipStatus.ACTIVE) is True

    def test_invited_to_revoked(self) -> None:
        assert can_transition_membership_status(MembershipStatus.INVITED, MembershipStatus.REVOKED) is True

    def test_active_to_suspended(self) -> None:
        assert can_transition_membership_status(MembershipStatus.ACTIVE, MembershipStatus.SUSPENDED) is True

    def test_suspended_to_active(self) -> None:
        assert can_transition_membership_status(MembershipStatus.SUSPENDED, MembershipStatus.ACTIVE) is True

    def test_revoked_is_terminal(self) -> None:
        assert can_transition_membership_status(MembershipStatus.REVOKED, MembershipStatus.ACTIVE) is False

    @pytest.mark.parametrize(
        ("current", "target"),
        [
            (MembershipStatus.ACTIVE, MembershipStatus.INVITED),
            (MembershipStatus.SUSPENDED, MembershipStatus.INVITED),
            (MembershipStatus.REVOKED, MembershipStatus.INVITED),
            (MembershipStatus.REVOKED, MembershipStatus.ACTIVE),
            (MembershipStatus.REVOKED, MembershipStatus.SUSPENDED),
        ],
    )
    def test_disallowed_membership_transitions(self, current: MembershipStatus, target: MembershipStatus) -> None:
        assert can_transition_membership_status(current, target) is False


class TestMembershipRevocationSafety:
    def test_cannot_revoke_last_owner(self) -> None:
        assert can_revoke_membership(MembershipRole.OWNER, total_active_owners=1) is False

    def test_can_revoke_owner_if_multiple_owners_exist(self) -> None:
        assert can_revoke_membership(MembershipRole.OWNER, total_active_owners=2) is True

    def test_can_revoke_non_owner_even_with_one_owner(self) -> None:
        assert can_revoke_membership(MembershipRole.MEMBER, total_active_owners=1) is True
        assert can_revoke_membership(MembershipRole.ADMIN, total_active_owners=1) is True


class TestMembershipAccessRule:
    def test_active_member_in_active_org_allowed(self) -> None:
        assert is_membership_allowed_access(MembershipStatus.ACTIVE, OrganizationStatus.ACTIVE) is True

    @pytest.mark.parametrize(
        ("mem_status", "org_status"),
        [
            (MembershipStatus.SUSPENDED, OrganizationStatus.ACTIVE),
            (MembershipStatus.INVITED, OrganizationStatus.ACTIVE),
            (MembershipStatus.REVOKED, OrganizationStatus.ACTIVE),
            (MembershipStatus.ACTIVE, OrganizationStatus.SUSPENDED),
            (MembershipStatus.ACTIVE, OrganizationStatus.PROVISIONING),
            (MembershipStatus.ACTIVE, OrganizationStatus.ARCHIVED),
        ],
    )
    def test_inactive_member_or_org_denied(
        self,
        mem_status: MembershipStatus,
        org_status: OrganizationStatus,
    ) -> None:
        assert is_membership_allowed_access(mem_status, org_status) is False
