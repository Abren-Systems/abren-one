# Recipe: Add a Model

## Steps

### 1. Identify the owning module

Every model belongs to exactly one module. Determine which module owns the entity:

- Business entities → `modules/<name>/`
- Platform infrastructure → `platform/<name>/`

No module may add fields to another module's models.

### 2. Create the model file

```
backend/src/abren_one/modules/<module>/models/<entity>.py
```

Use a `models/` package once a module has more than two entities.

### 3. Define the model

```python
import uuid

from django.db import models

from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class Branch(TimestampMixin, OrgOwnedMixin, models.Model):
    """A physical or logical branch within an organization."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "organizations"
        verbose_name_plural = "branches"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_branch_code_per_org",
            ),
        ]

    def __str__(self) -> str:
        return self.name
```

**Conventions:**

- UUID primary key: `id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`
- Add `TimestampMixin` for `created_at` / `updated_at` on records that change
- Add `OrgOwnedMixin` for tenant-scoped records (adds `organization` FK)
- Mixins are opt-in — define fields directly when a mixin doesn't fit

### 4. Register in `models/__init__.py`

Django discovers models via the app's `models` module. Every model class must be imported here:

```python
# modules/organizations/models/__init__.py
from abren_one.modules.organizations.models.organization import Organization
from abren_one.modules.organizations.models.branch import Branch
from abren_one.modules.organizations.models.membership import Membership

__all__ = ["Organization", "Branch", "Membership"]
```

### 5. Register in `admin.py` (optional)

```python
# modules/organizations/admin.py
from django.contrib import admin

from abren_one.modules.organizations.models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "organization", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
```

### 6. Create the migration

```bash
uv run python backend/manage.py makemigrations organizations --name create_branch
```

### 7. Review the migration file

Check for:

- Correct `app_label`
- Expected operations (CreateModel, AddField, etc.)
- No accidental changes to other models
- Correct FK references

### 8. Apply the migration

```bash
uv run python backend/manage.py migrate
```

### 9. Cross-module ForeignKeys

If the model has a FK to another module's model, use a string reference:

```python
# In modules/programs/models/program.py
organization = models.ForeignKey(
    "organizations.Organization",
    on_delete=models.PROTECT,
    related_name="+",
)
```

**Rules for cross-module FKs:**

- Use string-based references (`"app_label.ModelName"`) — do not import the other module's model
- Document the relationship in both modules' documentation
- The cross-module FK migration must be reviewed as an architectural change

## Complete Example: Branch Model

**File:** `backend/src/abren_one/modules/organizations/models/branch.py`

```python
import uuid

from django.db import models

from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class Branch(TimestampMixin, OrgOwnedMixin, models.Model):
    """
    A physical or logical branch within an organization.

    Branches represent distinct operational locations or units.
    Every branch belongs to exactly one organization (via OrgOwnedMixin).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(
        max_length=50,
        blank=True,
        help_text="Short identifier for the branch (e.g., 'HQ', 'NORTH-01').",
    )
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "organizations"
        verbose_name_plural = "branches"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                condition=models.Q(code__gt=""),
                name="unique_branch_code_per_org",
            ),
        ]

    def __str__(self) -> str:
        return self.name
```

**Update:** `backend/src/abren_one/modules/organizations/models/__init__.py`

```python
from abren_one.modules.organizations.models.branch import Branch

# ... existing imports ...
```

**Generate and apply:**

```bash
uv run python backend/manage.py makemigrations organizations --name create_branch
# Review the generated migration file
uv run python backend/manage.py migrate
```

## Rules

- Every model belongs to exactly one module
- UUID primary keys on all application-owned records
- `TimestampMixin` and `OrgOwnedMixin` are opt-in — not mandatory
- Monetary values: always `DecimalField` with explicit `max_digits` and `decimal_places` — **never `FloatField`**
- Financial records must include an explicit currency field alongside the amount
- Cross-module FKs use string references and require documentation in both modules
- Only the owning module may create migrations for its models
- Import all model classes in `models/__init__.py` for Django discovery
