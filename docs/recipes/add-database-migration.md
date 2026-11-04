# Recipe: Add a Database Migration

## Steps

### 1. Ensure the model change is in the correct module

Every model belongs to exactly one module. Only the owning module may create migrations for its models. Verify the model file is in:

```
backend/src/abren_one/modules/<module>/models/<entity>.py
```

And that it is imported in `models/__init__.py` for Django discovery.

### 2. Generate the migration

```bash
uv run python backend/manage.py makemigrations <app_label> --name <descriptive_name>
```

Use descriptive names that reflect the change:

```bash
# Good
uv run python backend/manage.py makemigrations organizations --name create_branch
uv run python backend/manage.py makemigrations programs --name add_budget_field_to_program
uv run python backend/manage.py makemigrations organizations --name make_branch_code_unique

# Bad
uv run python backend/manage.py makemigrations organizations
```

### 3. Review the generated migration

Open the generated file and check:

- **Correct `app_label`** — the migration is in the right module's `migrations/` directory
- **Expected operations** — only the changes you intended (CreateModel, AddField, AlterField, etc.)
- **No accidental changes** — no unintended model modifications pulled in
- **FK references** — cross-module ForeignKeys use the correct `"app_label.ModelName"` string
- **Dependencies** — if the migration references another module's model, the dependency is listed

### 4. Test forward migration

```bash
uv run python backend/manage.py migrate
```

Verify the migration applies cleanly with no errors.

### 5. Test backward migration

```bash
uv run python backend/manage.py migrate <app_label> <previous_migration_number>
```

Example:

```bash
# Roll back to migration 0003
uv run python backend/manage.py migrate organizations 0003
# Then re-apply
uv run python backend/manage.py migrate
```

Ensure the rollback applies cleanly. Some operations are not reversible by default — if your migration cannot be reversed, document why.

## Data Migrations

### Never combine schema and data migrations

Schema migrations (CreateModel, AddField, etc.) and data migrations (RunPython) must be in **separate** migration files. This keeps each migration focused and independently reversible.

### Create a data migration

```bash
uv run python backend/manage.py makemigrations <app_label> --empty --name populate_branch_codes
```

Then edit the generated file:

```python
from django.db import migrations


def populate_branch_codes(apps, schema_editor):
    Branch = apps.get_model("organizations", "Branch")
    for branch in Branch.objects.filter(code=""):
        branch.code = f"BR-{branch.name[:10].upper()}"
        branch.save(update_fields=["code"])


def reverse_populate_branch_codes(apps, schema_editor):
    Branch = apps.get_model("organizations", "Branch")
    Branch.objects.all().update(code="")


class Migration(migrations.Migration):
    dependencies = [
        ("organizations", "0004_add_code_to_branch"),
    ]

    operations = [
        migrations.RunPython(
            populate_branch_codes,
            reverse_populate_branch_codes,
        ),
    ]
```

**Data migration rules:**

- Always use `apps.get_model()` — never import models directly
- Always provide a `reverse` function (use `migrations.RunPython.noop` if reversal is truly impossible)
- Keep data migrations small and focused
- Test both forward and reverse execution

## Cross-Module FK Migrations

When a migration references a model from another module:

1. Django auto-detects the dependency and adds it to the migration's `dependencies` list
2. Verify the dependency is present: `("other_app_label", "migration_name")`
3. Document the cross-module relationship in both modules' documentation
4. Cross-module FK migrations require architectural review

Example dependency in a migration file:

```python
class Migration(migrations.Migration):
    dependencies = [
        ("programs", "0002_add_organization_fk"),
        ("organizations", "0003_create_branch"),  # Cross-module dependency
    ]
```

## Squashing Migrations

Once a module has accumulated many migrations, squash them to reduce migration count:

```bash
uv run python backend/manage.py squashmigrations <app_label> <start> <end>
```

Example:

```bash
uv run python backend/manage.py squashmigrations organizations 0001 0010
```

**After squashing:**

1. Review the squashed migration file
2. Test forward migration from scratch
3. Remove the `replaces` attribute and delete old migration files only after all environments have applied through the squashed range

## Troubleshooting

### "No changes detected"

- Verify the model is imported in `models/__init__.py`
- Verify `apps.py` has the correct `name` and the app is in `INSTALLED_APPS`
- Check the correct `app_label` is specified in the model's `Meta`

### Conflicting migrations

Two developers created migrations with the same number:

```bash
uv run python backend/manage.py makemigrations --merge
```

Review the merge migration and test it.

### Migration dependency errors

- Ensure cross-module dependencies are listed in the `dependencies` list
- Check for circular dependencies between modules — this may indicate an architectural issue

### "Table already exists"

If the table exists but Django doesn't know about it:

```bash
uv run python backend/manage.py migrate <app_label> <migration_number> --fake
```

> [!CAUTION]
> `--fake` marks a migration as applied without running it. Only use this when you are certain the database schema already matches the migration. Incorrect use will cause schema drift.

## Rules

- Only the owning module creates migrations for its models
- Always use descriptive `--name` for migrations
- Review every generated migration before applying
- Never combine schema and data migrations
- Test both forward and backward migration
- Cross-module FK migrations require architectural review and documentation in both modules
- Use `apps.get_model()` in data migrations — never direct model imports
- Migrations are reviewed as architectural changes
