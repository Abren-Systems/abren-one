# Migration Conventions

Migrations are a critical part of the architecture. They change the database schema and must be treated as architectural changes, not routine code.

---

## Ownership

- Migrations are **owned by the module that owns the model**
- Only the owning module may create migrations for its models
- No module may add fields to another module's models
- Cross-module ForeignKeys must be documented in both modules' documentation

## Creating Migrations

```bash
# Generate a migration for a specific app
uv run python backend/manage.py makemigrations <app_label> --name <descriptive_name>

# Examples
uv run python backend/manage.py makemigrations organizations --name add_branch_status_field
uv run python backend/manage.py makemigrations programs --name create_activity_model
```

**Always** provide a descriptive `--name`. Default names like `0002_auto_20261104` are not acceptable.

## Naming Convention

```
<number>_<descriptive_action>.py
```

Examples:
- `0001_initial.py`
- `0002_add_branch_status_field.py`
- `0003_create_membership_model.py`
- `0004_add_organization_slug_unique_constraint.py`

## Review Checklist

Before committing a migration, verify:

1. **Correct app label** — the migration belongs to the module that owns the model
2. **Expected operations** — only the intended changes are present
3. **No accidental changes** — no unrelated field alterations or model changes
4. **Cross-module FKs** — if referencing another module's model, it uses a string reference
5. **Reversibility** — the migration can be rolled back cleanly

## Schema vs. Data Migrations

**Never combine schema and data migrations in the same file.**

Schema migrations change the database structure (add/remove fields, tables, indexes). Data migrations transform existing data (populate new fields, restructure records).

```bash
# Create an empty migration for data-only operations
uv run python backend/manage.py makemigrations <app_label> --empty --name populate_branch_slugs
```

```python
# Example data migration
from django.db import migrations


def populate_slugs(apps, schema_editor):
    Branch = apps.get_model("organizations", "Branch")
    for branch in Branch.objects.filter(slug=""):
        branch.slug = branch.name.lower().replace(" ", "-")
        branch.save(update_fields=["slug"])


def reverse_populate_slugs(apps, schema_editor):
    pass  # No meaningful reverse for this


class Migration(migrations.Migration):
    dependencies = [
        ("organizations", "0005_add_branch_slug"),
    ]
    operations = [
        migrations.RunPython(populate_slugs, reverse_populate_slugs),
    ]
```

## Testing Migrations

```bash
# Apply forward
uv run python backend/manage.py migrate

# Check migration status
uv run python backend/manage.py showmigrations

# Test rollback to a specific migration
uv run python backend/manage.py migrate <app_label> <previous_number>
# Example: roll back to migration 0003
uv run python backend/manage.py migrate organizations 0003
```

## Squashing

When migration history becomes unwieldy (typically 20+ migrations per app):

```bash
uv run python backend/manage.py squashmigrations <app_label> <start> <end>
```

Squashing combines multiple migrations into one while preserving the same database state. Review the squashed migration carefully — `RunPython` operations may need manual attention.

## Monetary Fields

All monetary fields must use `DecimalField` with explicit precision:

```python
amount = models.DecimalField(max_digits=15, decimal_places=2)
currency = models.CharField(max_length=3)  # ISO 4217
```

**Never** use `FloatField` for monetary values. Every monetary field requires an accompanying currency field.

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Editing an applied migration | Create a new migration instead |
| Missing reverse operations | Always define a reverse function (even if it's a no-op) |
| Non-atomic data migration on large tables | Use `migrations.RunPython(..., atomic=False)` and batch processing |
| Forgetting to import in `models/__init__.py` | Django won't discover the model without it |
| Circular migration dependencies | Use string-based FK references, restructure dependency order |
