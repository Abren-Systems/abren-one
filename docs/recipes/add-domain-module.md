# Recipe: Add a Domain Module

## Steps

### 1. Create the directory structure

```bash
MODULE=fundraising  # replace with your module name
mkdir -p backend/src/abren_one/modules/$MODULE/{models,domain,application/{commands,queries},infrastructure,interfaces/api/v1,migrations,tests/{unit,integration,api}}
```

### 2. Create `__init__.py` files

```bash
find backend/src/abren_one/modules/$MODULE -type d -exec touch {}/__init__.py \;
```

### 3. Create `apps.py`

```python
# backend/src/abren_one/modules/<name>/apps.py
from django.apps import AppConfig


class FundraisingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "abren_one.modules.fundraising"
    label = "fundraising"
    verbose_name = "Fundraising"
```

### 4. Create `public.py`

```python
# backend/src/abren_one/modules/<name>/public.py
"""Public interface for the Fundraising module."""

__all__: list[str] = []
```

### 5. Register in settings

Add to `MODULE_APPS` in `backend/config/settings/base.py`:

```python
MODULE_APPS = [
    "abren_one.modules.fundraising",
]
```

### 6. Create module documentation

Create `docs/modules/fundraising/module.md` with purpose, ownership, and public interface.

### 7. Verify

```bash
uv run python backend/manage.py check --settings=config.settings.local
uv run pytest backend/tests/architecture/ -p no:django
uv run lint-imports
```

## Checklist

- [ ] Directory structure matches convention
- [ ] `apps.py` has correct `name` and `label`
- [ ] `public.py` exists
- [ ] Registered in `INSTALLED_APPS`
- [ ] Module documentation created
- [ ] Architecture tests pass
- [ ] Import-linter contracts pass
