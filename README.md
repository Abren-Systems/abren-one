# Abren One

**NGO Operating System** — A domain-oriented modular monolith built with Django.

## Tech Stack

| Component | Version |
|-----------|---------|
| Python | 3.15 |
| Django | 6.1.3 |
| Django REST Framework | 3.18.3 |
| PostgreSQL | 15+ |
| Vue 3 + TypeScript | (frontend) |
| uv | Package management |

## Quick Start

```bash
# Clone and install
git clone <repo-url> && cd abren-one
uv sync

# Run Django checks
uv run python backend/manage.py check --settings=config.settings.local

# Run tests
uv run pytest

# Run architecture enforcement
uv run lint-imports
uv run pytest backend/tests/architecture/ -p no:django

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Architecture

Abren One is a **domain-oriented modular monolith** with explicit module boundaries, vertical-slice implementation patterns, and automated architecture enforcement.

See [docs/architecture/](docs/architecture/) for the full specification.

## Repository Structure

```
abren-one/
├── backend/          # Django application
│   ├── config/       # Django settings and URL configuration
│   └── src/
│       └── abren_one/
│           ├── platform/    # Cross-cutting infrastructure
│           ├── modules/     # Business domain capabilities
│           └── integrations/ # External system adapters
├── frontend/         # Vue 3 + TypeScript
├── docs/             # Architecture, engineering, recipes
├── engineering/      # Standards, agent task artifacts
└── infra/            # Deployment configuration
```
