# Implementation Workflow

Step-by-step workflow for implementing a feature in Abren One.

---

## 1. Identify the Owning Module

Every feature belongs to exactly one module. Determine:

- Which business domain does this feature serve?
- Which module owns the primary data?
- Does this feature require cross-module collaboration?

If cross-module collaboration is needed, the orchestrating module owns the feature and accesses other modules through their `public.py`.

## 2. Define Domain Concepts

If the feature introduces new business rules:

```
modules/<name>/domain/
├── policies.py       # Business rules and validations
├── services.py       # Domain operations
├── events.py         # Domain events
├── exceptions.py     # Domain-specific errors
└── value_objects.py  # Immutable value types
```

Domain code must **not** depend on Django ORM, DRF, HTTP, or external infrastructure.

## 3. Create or Update Models

If the feature requires new or modified data structures:

1. Create/modify model in `modules/<name>/models/<entity>.py`
2. Import in `models/__init__.py` for Django discovery
3. Generate migration: `uv run python backend/manage.py makemigrations <app_label> --name <descriptive_name>`
4. Review the migration file
5. Apply: `uv run python backend/manage.py migrate`

See [Add Model recipe](../recipes/add-model.md) and [Migration conventions](migrations.md).

## 4. Write the Application Operation

### For state-changing operations → Command

Create in `modules/<name>/application/commands/<verb>_<entity>.py`:

```python
@dataclass(frozen=True)
class CreateBranchInput:
    context: ExecutionContext
    name: str
    # ...


@dataclass(frozen=True)
class CreateBranchResult:
    branch_id: UUID


@transaction.atomic
def execute(data: CreateBranchInput) -> CreateBranchResult:
    # 1. Verify authorization
    # 2. Validate business rules
    # 3. Persist state
    # 4. Record audit event
    # 5. Return result
    ...
```

See [Add Command recipe](../recipes/add-command.md).

### For read operations → Query

Create in `modules/<name>/application/queries/<verb>_<entity>.py`:

```python
@dataclass(frozen=True)
class GetBranchResult:
    id: UUID
    name: str
    # ...


def execute(*, branch_id: UUID, organization_id: UUID) -> GetBranchResult: ...
```

See [Add Query recipe](../recipes/add-query.md).

## 5. Create the API Endpoint

Create in `modules/<name>/interfaces/api/v1/`:

1. Add serializers in `serializers.py`
2. Add view in `views.py`
3. Add URL pattern in `urls.py`
4. Add permissions in `permissions.py` if needed

Views delegate to application operations — they do **not** contain business logic.

See [Add API Endpoint recipe](../recipes/add-api-endpoint.md).

## 6. Write Tests

Write tests in order of speed and isolation:

### Unit tests (no database)
```
modules/<name>/tests/unit/test_<feature>.py
```
Test domain policies, value objects, and pure business logic.

### Integration tests (with database)
```
modules/<name>/tests/integration/test_<feature>.py
```
Test commands and queries against a real database.

### API tests (full HTTP)
```
modules/<name>/tests/api/test_<feature>.py
```
Test the API endpoint with DRF's test client. Include:
- Happy path
- Input validation errors
- Authorization failures
- **Cross-tenant access denial** (mandatory for tenant-scoped endpoints)

## 7. Update Public Interface

If this feature is consumed by other modules, update `public.py`:

```python
# modules/<name>/public.py
from abren_one.modules.<name>.application.queries.<query> import (
    <query_function>,
    <ResultDTO>,
)

__all__ = ["<query_function>", "<ResultDTO>"]
```

Remember: `public.py` exposes **capabilities** (queries, commands, DTOs), not ORM models.

## 8. Run Verification Suite

```bash
# Architecture enforcement
uv run pytest backend/tests/architecture/ -p no:django

# Import boundary checks
uv run lint-imports

# Linting
uv run ruff check .

# Type checking
uv run pyright

# All tests
uv run pytest
```

All checks must pass before the feature is considered complete.

## 9. Update Documentation

- Update the module's documentation in `docs/modules/<name>/module.md`
- If a cross-module FK was added, document it in both modules
- If the public interface changed, update consumer documentation

## Checklist

- [ ] Feature belongs to the correct module
- [ ] Domain rules are in `domain/`, not in views or serializers
- [ ] Command/query follows the established patterns
- [ ] Views only validate input, build context, and delegate
- [ ] Unit, integration, and API tests written
- [ ] Cross-tenant negative test exists (for tenant-scoped features)
- [ ] `public.py` updated if cross-module
- [ ] Architecture tests pass
- [ ] Import-linter passes
- [ ] Ruff passes
- [ ] Module documentation updated
