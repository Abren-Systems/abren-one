# Django Conventions

## Settings

- Split into `base.py`, `local.py`, `test.py`, `production.py`
- No secrets in files — use `os.environ`
- Custom user model: `AUTH_USER_MODEL = "identity.User"`

## Apps

- One Django app per meaningful domain module
- `AppConfig` in `apps.py` with explicit `name` and `label`
- Register in `INSTALLED_APPS` only when the app has models/migrations

## Models

- Use `models/` package (not single `models.py`) once you have >2 entities
- `models/__init__.py` must import all model classes for Django discovery
- UUID primary keys, `created_at`/`updated_at` as applicable

## Commands and Queries

- Commands: `application/commands/<verb>_<entity>.py` — `@transaction.atomic`, frozen dataclass input with `ExecutionContext`
- Queries: `application/queries/<verb>_<entity>.py` — return DTOs for cross-module, model instances OK within same module
- No DRF imports in application or domain layers

## Migrations

- Review as architectural changes
- Only the owning module creates migrations for its models
- Cross-module FK migration dependencies must be documented
