# Python Conventions

**Runtime:** Python 3.15  
**Package manager:** uv (never pip, never `/usr/bin/python3`)  
**Linter/formatter:** ruff  
**Type checker:** pyright (strict mode)

---

## Style and Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Functions, variables | `snake_case` | `get_organization`, `org_id` |
| Classes | `PascalCase` | `Organization`, `ExecutionContext` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT`, `DEFAULT_CURRENCY` |
| Modules, packages | `snake_case` | `record_donation.py` |
| Type aliases | `PascalCase` | `OrganizationId = UUID` |

## Type Hints

Use modern Python 3.10+ syntax — **do not** use `typing` equivalents:

```python
# ✅ Correct
def get_user(user_id: UUID) -> User | None: ...
items: list[str] = []
mapping: dict[str, int] = {}

# ❌ Wrong — do not use Optional, List, Dict, Union
from typing import Optional, List, Dict, Union
def get_user(user_id: UUID) -> Optional[User]: ...
```

All public functions must have type annotations for parameters and return values.

## Imports

Import order is enforced by ruff (isort-compatible):

1. Standard library
2. Third-party packages
3. Project imports (`abren_one.*`)

```python
import uuid
from dataclasses import dataclass
from decimal import Decimal

from django.db import models

from abren_one.platform.common.context import ExecutionContext
```

Rules:
- **No wildcard imports** (`from module import *`)
- **No relative imports** — use absolute imports from `abren_one`
- `public.py` files must define `__all__`

## Data Structures

### DTOs and Value Objects

Use frozen dataclasses for data transfer objects and value objects:

```python
from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class GetOrganizationResult:
    id: UUID
    name: str
    slug: str
    is_active: bool
```

### Enumerations

Use `StrEnum` for enumerated values — not plain strings or `Enum`:

```python
from enum import StrEnum

class MembershipStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
```

### Identifiers

Use `UUID` (generated via `uuid.uuid4`) for all application-owned record identifiers:

```python
import uuid
from django.db import models

class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```

## Monetary Values

**Always** use `Decimal` — **never** `float` for monetary values:

```python
from decimal import Decimal
from django.db import models

class Donation(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3)  # ISO 4217
```

Every monetary field must have an accompanying explicit currency field.

## String Formatting

Prefer f-strings for string interpolation:

```python
# ✅ Preferred
message = f"Organization {org.name} created by {actor_id}"

# ❌ Avoid
message = "Organization {} created by {}".format(org.name, actor_id)
message = "Organization %s created by %s" % (org.name, actor_id)
```

## Design Principles

- **Prefer composition over inheritance** — use mixins sparingly and deliberately
- **Explicit over implicit** — pass dependencies, don't rely on global state
- **One command/query per file** — keeps application operations discoverable
- **Frozen dataclasses for boundaries** — inputs, outputs, and value objects are immutable
- **Fail loudly** — raise explicit exceptions, don't return `None` to signal errors

## Running Tools

```bash
# Linting
uv run ruff check .
uv run ruff check --fix .

# Formatting
uv run ruff format .

# Type checking
uv run pyright

# Tests
uv run pytest

# Architecture tests (no Django needed)
uv run pytest backend/tests/architecture/ -p no:django

# Import boundary checks
uv run lint-imports
```
