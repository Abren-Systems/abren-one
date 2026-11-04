# Recipe: Add a Query

## Steps

### 1. Create the query file

```
backend/src/abren_one/modules/<module>/application/queries/<verb>_<entity>.py
```

### 2. Define the result DTO and execute function

```python
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetProgramResult:
    id: UUID
    name: str
    description: str
    is_active: bool


def execute(*, organization_id: UUID, program_id: UUID) -> GetProgramResult:
    """Retrieve a program by ID within an organization."""
    from abren_one.modules.programs.models import Program

    program = Program.objects.get(id=program_id, organization_id=organization_id)
    return GetProgramResult(
        id=program.id,
        name=program.name,
        description=program.description,
        is_active=program.is_active,
    )
```

### 3. Expose in `public.py` (if cross-module)

```python
from abren_one.modules.programs.application.queries.get_program import (
    get_program,
    GetProgramResult,
)
```

## Rules

- Return DTOs for cross-module queries, model instances OK within same module
- No state changes
- Tenant scoping is explicit (filter by `organization_id`)
- No DRF imports
