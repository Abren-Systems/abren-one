import uuid
from types import SimpleNamespace

import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from rest_framework.exceptions import PermissionDenied

from abren_one.platform.tenancy.context import (
    HEADER_ORGANIZATION_ID,
    extract_organization_id,
    get_current_organization_id,
)
from abren_one.platform.tenancy.exceptions import TenantContextInvalidError
from abren_one.platform.tenancy.middleware import TenantContextMiddleware
from abren_one.platform.tenancy.permissions import HasOrganizationContext
from abren_one.platform.tenancy.verifier import (
    MembershipInfo,
    register_membership_verifier,
)


class DummyVerifier:
    def __init__(self, memberships: dict[tuple[uuid.UUID, uuid.UUID], MembershipInfo]) -> None:
        self.memberships = memberships

    def get_membership(self, *, user_id: uuid.UUID, organization_id: uuid.UUID) -> MembershipInfo | None:
        return self.memberships.get((user_id, organization_id))


class TestExtractOrganizationId:
    def test_extract_valid_id_from_headers(self) -> None:
        factory = RequestFactory()
        org_id = uuid.uuid4()
        request = factory.get("/", headers={HEADER_ORGANIZATION_ID: str(org_id)})
        assert extract_organization_id(request) == org_id

    def test_extract_missing_returns_none(self) -> None:
        factory = RequestFactory()
        request = factory.get("/")
        assert extract_organization_id(request) is None

    def test_extract_invalid_raises_error(self) -> None:
        factory = RequestFactory()
        request = factory.get("/", headers={HEADER_ORGANIZATION_ID: "invalid-uuid"})
        with pytest.raises(TenantContextInvalidError):
            extract_organization_id(request)


class TestTenantContextMiddleware:
    def test_middleware_attaches_requested_org_and_cleans_up(self) -> None:
        factory = RequestFactory()
        org_id = uuid.uuid4()
        request = factory.get("/", headers={HEADER_ORGANIZATION_ID: str(org_id)})

        context_during_request = None

        def get_response(req):
            nonlocal context_during_request
            context_during_request = get_current_organization_id()
            return HttpResponse("ok")

        middleware = TenantContextMiddleware(get_response)
        response = middleware(request)

        assert response.status_code == 200
        assert request.requested_organization_id == org_id
        assert context_during_request == org_id
        assert get_current_organization_id() is None

    def test_middleware_handles_malformed_header(self) -> None:
        factory = RequestFactory()
        request = factory.get("/", headers={HEADER_ORGANIZATION_ID: "malformed"})

        def get_response(req):
            return HttpResponse("ok")

        middleware = TenantContextMiddleware(get_response)
        middleware(request)

        assert request.requested_organization_id is None
        assert get_current_organization_id() is None


class TestHasOrganizationContextPermission:
    def test_unauthenticated_user_denied(self) -> None:
        factory = RequestFactory()
        request = factory.get("/")
        request.user = SimpleNamespace(is_authenticated=False)

        perm = HasOrganizationContext()
        assert perm.has_permission(request, None) is False

    def test_missing_header_denied(self) -> None:
        factory = RequestFactory()
        request = factory.get("/")
        request.user = SimpleNamespace(is_authenticated=True, id=uuid.uuid4())

        perm = HasOrganizationContext()
        with pytest.raises(PermissionDenied, match="request header is required"):
            perm.has_permission(request, None)

    def test_malformed_header_denied(self) -> None:
        factory = RequestFactory()
        request = factory.get("/", headers={HEADER_ORGANIZATION_ID: "bad"})
        request.user = SimpleNamespace(is_authenticated=True, id=uuid.uuid4())

        perm = HasOrganizationContext()
        with pytest.raises(PermissionDenied, match="Malformed organization ID"):
            perm.has_permission(request, None)

    def test_user_not_member_denied(self) -> None:
        factory = RequestFactory()
        org_id = uuid.uuid4()
        user_id = uuid.uuid4()
        request = factory.get("/", headers={HEADER_ORGANIZATION_ID: str(org_id)})
        request.user = SimpleNamespace(is_authenticated=True, id=user_id)

        register_membership_verifier(DummyVerifier({}))

        perm = HasOrganizationContext()
        with pytest.raises(PermissionDenied, match="do not have active membership"):
            perm.has_permission(request, None)

    def test_inactive_membership_denied(self) -> None:
        factory = RequestFactory()
        org_id = uuid.uuid4()
        user_id = uuid.uuid4()
        request = factory.get("/", headers={HEADER_ORGANIZATION_ID: str(org_id)})
        request.user = SimpleNamespace(is_authenticated=True, id=user_id)

        info = MembershipInfo(
            organization_id=org_id,
            user_id=user_id,
            role="member",
            status="suspended",
            is_active=False,
        )
        register_membership_verifier(DummyVerifier({(user_id, org_id): info}))

        perm = HasOrganizationContext()
        with pytest.raises(PermissionDenied, match="do not have active membership"):
            perm.has_permission(request, None)

    def test_active_membership_granted(self) -> None:
        factory = RequestFactory()
        org_id = uuid.uuid4()
        user_id = uuid.uuid4()
        request = factory.get("/", headers={HEADER_ORGANIZATION_ID: str(org_id)})
        request.user = SimpleNamespace(is_authenticated=True, id=user_id)

        info = MembershipInfo(
            organization_id=org_id,
            user_id=user_id,
            role="owner",
            status="active",
            is_active=True,
        )
        register_membership_verifier(DummyVerifier({(user_id, org_id): info}))

        perm = HasOrganizationContext()
        assert perm.has_permission(request, None) is True
        assert hasattr(request, "org_context")
        assert request.org_context.organization_id == org_id
        assert request.org_context.role == "owner"
