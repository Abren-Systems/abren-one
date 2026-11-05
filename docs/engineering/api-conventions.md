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

Every view constructs an `ExecutionContext` before calling the application layer:

```python
from abren_one.platform.common.context import ActorType, ExecutionContext

context = ExecutionContext(
    actor_type=ActorType.USER,
    actor_id=request.user.id,
    organization_id=request.org_context.organization_id,
    correlation_id=request.correlation_id,
)
result = execute(CreateProgramInput(context=context, ...))
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
