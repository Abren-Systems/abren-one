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

### 6. Update architecture enforcement

**Import-linter contracts** — add to `pyproject.toml`:

```toml
# Layer direction for the new module
[[tool.importlinter.contracts]]
name = "<Module> internal layer direction"
type = "layers"
layers = [
    "abren_one.modules.<name>.interfaces",
    "abren_one.modules.<name>.application",
    "abren_one.modules.<name>.domain",
]

# Add domain/application to the DRF-forbidden contract
# In the existing "Business domain/application layers do not import DRF" contract,
# append to source_modules:
#     "abren_one.modules.<name>.domain",
#     "abren_one.modules.<name>.application",
```

**Architecture tests** — update `backend/tests/architecture/test_structure.py`:

- Add the new module name to the `expected` set in `TestBusinessModulesExist.test_initial_business_modules`.

### 7. Create module documentation

Create `docs/modules/<name>/module.md` with purpose, ownership, and public interface.

### 8. Update agent instructions

If the module introduces new conventions or dependencies, update `backend/AGENTS.md`.

### 9. Verify

```bash
uv run python backend/manage.py check --settings=config.settings.local
uv run pytest backend/tests/architecture/ -p no:django
uv run lint-imports
```

## Checklist

- [ ] Directory structure matches convention
- [ ] `apps.py` has correct `name` and `label` (no `default_auto_field` — inherited from settings)
- [ ] `public.py` exists
- [ ] Registered in `INSTALLED_APPS` (`MODULE_APPS` in `base.py`)
- [ ] Import-linter layer contract added
- [ ] DRF-forbidden contract updated with new domain/application paths
- [ ] `TestBusinessModulesExist` expected set updated
- [ ] Module documentation created
- [ ] `backend/AGENTS.md` updated if needed
- [ ] Architecture tests pass
- [ ] Import-linter contracts pass
