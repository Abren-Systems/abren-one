import uuid
from types import SimpleNamespace

from django.http import HttpResponse
from django.test import RequestFactory

from abren_one.platform.common.context import ActorType, build_execution_context
from abren_one.platform.common.middleware import CORRELATION_HEADER, CorrelationMiddleware
from abren_one.platform.tenancy.context import OrganizationContext


class TestCorrelationMiddleware:
    def test_generates_correlation_id_when_missing(self) -> None:
        factory = RequestFactory()
        request = factory.get("/")

        def get_response(req):
            return HttpResponse("ok")

        middleware = CorrelationMiddleware(get_response)
        response = middleware(request)

        assert hasattr(request, "correlation_id")
        assert isinstance(request.correlation_id, uuid.UUID)
        assert response[CORRELATION_HEADER] == str(request.correlation_id)

    def test_accepts_valid_correlation_id_header(self) -> None:
        factory = RequestFactory()
        custom_id = uuid.uuid4()
        request = factory.get("/", HTTP_X_CORRELATION_ID=str(custom_id))

        def get_response(req):
            return HttpResponse("ok")

        middleware = CorrelationMiddleware(get_response)
        response = middleware(request)

        assert request.correlation_id == custom_id
        assert response[CORRELATION_HEADER] == str(custom_id)

    def test_replaces_malformed_correlation_id(self) -> None:
        factory = RequestFactory()
        request = factory.get("/", HTTP_X_CORRELATION_ID="not-a-valid-uuid")

        def get_response(req):
            return HttpResponse("ok")

        middleware = CorrelationMiddleware(get_response)
        response = middleware(request)

        assert isinstance(request.correlation_id, uuid.UUID)
        assert str(request.correlation_id) != "not-a-valid-uuid"
        assert response[CORRELATION_HEADER] == str(request.correlation_id)


class TestBuildExecutionContext:
    def test_unauthenticated_request(self) -> None:
        factory = RequestFactory()
        request = factory.get("/")
        request.user = SimpleNamespace(is_authenticated=False)
        request.correlation_id = uuid.uuid4()

        context = build_execution_context(request)
        assert context.actor_type == ActorType.USER
        assert context.actor_id is None
        assert context.organization_id is None
        assert context.correlation_id == request.correlation_id

    def test_authenticated_user_without_org(self) -> None:
        factory = RequestFactory()
        user_id = uuid.uuid4()
        request = factory.get("/")
        request.user = SimpleNamespace(is_authenticated=True, id=user_id)
        request.correlation_id = uuid.uuid4()

        context = build_execution_context(request)
        assert context.actor_type == ActorType.USER
        assert context.actor_id == user_id
        assert context.organization_id is None
        assert context.correlation_id == request.correlation_id

    def test_authenticated_user_with_org_context(self) -> None:
        factory = RequestFactory()
        user_id = uuid.uuid4()
        org_id = uuid.uuid4()
        request = factory.get("/")
        request.user = SimpleNamespace(is_authenticated=True, id=user_id)
        request.org_context = OrganizationContext(organization_id=org_id, role="admin")
        request.correlation_id = uuid.uuid4()

        context = build_execution_context(request)
        assert context.actor_type == ActorType.USER
        assert context.actor_id == user_id
        assert context.organization_id == org_id
        assert context.correlation_id == request.correlation_id

    def test_authenticated_staff_or_superuser_is_administrator(self) -> None:
        factory = RequestFactory()
        user_id = uuid.uuid4()
        request = factory.get("/")
        request.user = SimpleNamespace(is_authenticated=True, id=user_id, is_staff=True, is_superuser=False)
        request.correlation_id = uuid.uuid4()

        context = build_execution_context(request)
        assert context.actor_type == ActorType.ADMINISTRATOR
        assert context.actor_id == user_id

    def test_system_actor_detected(self) -> None:
        factory = RequestFactory()
        request = factory.get("/")
        request.user = SimpleNamespace(is_authenticated=False)
        request.is_system = True
        request.correlation_id = uuid.uuid4()

        context = build_execution_context(request)
        assert context.actor_type == ActorType.SYSTEM
        assert context.actor_id is None

    def test_integration_actor_detected(self) -> None:
        factory = RequestFactory()
        request = factory.get("/")
        request.user = SimpleNamespace(is_authenticated=False)
        request.is_integration = True
        request.correlation_id = uuid.uuid4()

        context = build_execution_context(request)
        assert context.actor_type == ActorType.INTEGRATION
        assert context.actor_id is None
