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

# Run all validation gates (CI parity)
./scripts/validate.sh

# Or run individual checks
uv run python backend/manage.py check --settings=config.settings.local
uv run pytest
uv run lint-imports
uv run ruff check .
uv run ruff format .
uv run pyright
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
