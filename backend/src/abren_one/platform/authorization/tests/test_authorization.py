import uuid

from django.test import RequestFactory

from abren_one.platform.authorization.evaluator import has_permission, has_role
from abren_one.platform.authorization.permissions import require_permission, require_role
from abren_one.platform.authorization.roles import Role
from abren_one.platform.tenancy.context import OrganizationContext


class TestAuthorizationEvaluator:
    def test_has_role(self) -> None:
        assert has_role(None, ["owner"]) is False
        assert has_role("", ["owner"]) is False
        assert has_role("owner", ["owner", "admin"]) is True
        assert has_role("OWNER", ["owner"]) is True  # case insensitive
        assert has_role("member", ["owner", "admin"]) is False

    def test_has_permission_owner_implicit_wildcard(self) -> None:
        assert has_permission(Role.OWNER.value, "any:arbitrary:permission") is True
        assert has_permission("OWNER", "any:arbitrary:permission") is True

    def test_has_permission_mapped_roles(self) -> None:
        assert has_permission("admin", "organizations:manage") is True
        assert has_permission("member", "organizations:manage") is False
        assert has_permission("member", "organizations:view") is True

    def test_has_permission_none_or_unknown(self) -> None:
        assert has_permission(None, "organizations:view") is False
        assert has_permission("member", "nonexistent:permission") is False


class TestAuthorizationPermissions:
    def test_require_role_factory_grants_allowed_role(self) -> None:
        factory = RequestFactory()
        request = factory.get("/")
        request.org_context = OrganizationContext(
            organization_id=uuid.uuid4(),
            role="admin",
        )

        perm_class = require_role("owner", "admin")
        perm = perm_class()
        assert perm.has_permission(request, None) is True

    def test_require_role_factory_denies_disallowed_role(self) -> None:
        factory = RequestFactory()
        request = factory.get("/")
        request.org_context = OrganizationContext(
            organization_id=uuid.uuid4(),
            role="member",
        )

        perm_class = require_role("owner", "admin")
        perm = perm_class()
        assert perm.has_permission(request, None) is False

    def test_require_role_factory_denies_missing_org_context(self) -> None:
        factory = RequestFactory()
        request = factory.get("/")

        perm_class = require_role("owner")
        perm = perm_class()
        assert perm.has_permission(request, None) is False

    def test_require_permission_factory_grants_and_denies(self) -> None:
        factory = RequestFactory()
        perm_class = require_permission("organizations:manage")
        perm = perm_class()

        # Admin has permission
        req1 = factory.get("/")
        req1.org_context = OrganizationContext(organization_id=uuid.uuid4(), role="admin")
        assert perm.has_permission(req1, None) is True

        # Member does not have organizations:manage
        req2 = factory.get("/")
        req2.org_context = OrganizationContext(organization_id=uuid.uuid4(), role="member")
        assert perm.has_permission(req2, None) is False

        # Request without org_context
        req3 = factory.get("/")
        assert perm.has_permission(req3, None) is False
