# Abren One Backend — Agent Instructions

## Module Structure Convention

Every module (platform/ or modules/) follows this pattern:
```
module_name/
├── __init__.py
├── apps.py          # Django AppConfig
├── public.py        # Cross-module interface (business modules only)
├── models/          # Django ORM models
├── domain/          # Business rules, policies, value objects
├── application/     # Commands and queries (vertical slices)
│   ├── commands/    # State-changing operations
│   └── queries/     # Read operations
├── infrastructure/  # External adapters, background tasks
├── interfaces/      # API endpoints
│   └── api/v1/
├── migrations/
└── tests/
```

## Dependency Direction

- **Interfaces** → Application → Domain (domain never imports DRF/HTTP)
- Application may use Django ORM models directly (no mandatory repositories)
- Cross-module imports: use `public.py` only, or string-based FK references

## Commands Pattern

```python
@dataclass(frozen=True)
class CreateThingInput:
    context: ExecutionContext  # from platform.common.context
    name: str


@transaction.atomic
def execute(data: CreateThingInput) -> CreateThingResult: ...
```

## Settings

- Local: `config.settings.local` (SQLite, DEBUG=True)
- Test: `config.settings.test` (in-memory SQLite, fast hasher)
- Production: `config.settings.production` (PostgreSQL, env vars required)

## Running

```bash
uv run python backend/manage.py <command> --settings=config.settings.local
uv run pytest
uv run lint-imports
```
