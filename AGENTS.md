# Abren One — Agent Instructions

## Architecture

Abren One is a domain-oriented modular monolith. The architecture docs in `docs/architecture/` are derived from the approved Stage 0 Architecture Contracts. Read the architecture docs before making changes:

- [Architecture Overview](docs/architecture/architecture-overview.md)
- [Dependency Rules](docs/architecture/dependency-rules.md)
- [Module Map](docs/architecture/module-map.md)
- [Authorization Model](docs/architecture/authorization-model.md)
- [Transaction Model](docs/architecture/transaction-model.md)
- [Financial Architecture](docs/architecture/financial-architecture.md)
- [Data Ownership](docs/architecture/data-ownership.md)

## Critical Rules

1. **Module boundaries are enforced** — `import-linter` and architecture tests run in CI
2. **Cross-module imports go through `public.py`** — never import another module's internals
3. **Platform cannot depend on business modules** — dependency direction is enforced
4. **Business logic stays out of DRF views/serializers** — views delegate to application commands/queries
5. **Custom user model** — `AUTH_USER_MODEL = "identity.User"` is already configured
6. **No secrets in settings** — use environment variables

## Backend Details

See [backend/AGENTS.md](backend/AGENTS.md) for Django-specific conventions.

## Tooling

- **Package manager:** `uv` (never use pip directly)
- **Python:** 3.15 via uv
- **Linting:** `uv run ruff check .`
- **Type checking:** `uv run pyright`
- **Tests:** `uv run pytest`
- **Import contracts:** `uv run lint-imports`
