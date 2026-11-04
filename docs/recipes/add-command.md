# Recipe: Add a Command

## Steps

### 1. Create the command file

```
backend/src/abren_one/modules/<module>/application/commands/<verb>_<entity>.py
```

### 2. Define the input, result, and execute function

```python
from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateProgramInput:
    context: ExecutionContext
    name: str
    description: str


@dataclass(frozen=True)
class CreateProgramResult:
    program_id: UUID


@transaction.atomic
def execute(data: CreateProgramInput) -> CreateProgramResult:
    """
    Create a new program.

    Invariants:
    - Organization context must be non-null.
    - Actor must be authorized to create programs.
    - Program name must be unique within the organization.
    """
    assert data.context.organization_id is not None

    # 1. Verify actor authorization
    # 2. Validate business rules
    # 3. Persist state
    # 4. Record audit event
    # 5. Return result
    ...
```

### 3. Expose in `public.py` (if cross-module)

```python
from abren_one.modules.programs.application.commands.create_program import (
    create_program,
    CreateProgramInput,
    CreateProgramResult,
)
```

### 4. Write tests

```python
# modules/<module>/tests/unit/test_create_program.py
```

## Rules

- One file per command
- Frozen dataclass inputs — no HTTP coupling
- `ExecutionContext` carries verified identity
- `@transaction.atomic` for the operation boundary
- No DRF imports
