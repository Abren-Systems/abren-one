# API Conventions

## Structure

```
interfaces/api/v1/
├── urls.py         # URL routing
├── views.py        # Endpoint handlers
├── serializers.py  # Input validation + output formatting
├── permissions.py  # API-level access control
└── schemas.py      # OpenAPI customizations (when needed)
```

## View Responsibilities

A DRF view does **exactly** this:

1. Validate input using a serializer
2. Extract authenticated user and organization context
3. Construct `ExecutionContext`
4. Call the application command or query
5. Return the serialized result

## ExecutionContext Construction

Every view constructs an `ExecutionContext` using the shared platform helper before calling the application layer:

```python
from abren_one.platform.common.context import build_execution_context

context = build_execution_context(request)
result = execute(CreateProgramInput(context=context, ...))
```

If manual construction is required:

```python
from abren_one.platform.common.context import ActorType, ExecutionContext

context = ExecutionContext(
    actor_type=ActorType.USER,
    actor_id=request.user.id if request.user.is_authenticated else None,
    organization_id=getattr(request.org_context, "organization_id", None),
    correlation_id=getattr(request, "correlation_id", uuid.uuid4()),
)
```

## What Views Must NOT Contain

- Business rule validation beyond input format
- Direct ORM queries
- Transaction management
- Domain policy checks
- Cross-module orchestration
- Audit event recording

## Standards

| Convention | Standard |
| ------------ | ---------- |
| Versioning | URL path prefix: `/api/v1/` |
| Content type | `application/json` |
| Error format | `{"code": "...", "message": "...", "details": [...]}` |
| Pagination | Cursor-based for large collections |
| Authentication | Django session + CSRF (same-origin Vue app) |
| Tenant context | `X-Organization-ID` request header |
| OpenAPI | Generated and validated; serves as frontend contract |
