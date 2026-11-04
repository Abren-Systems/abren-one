# Testing Strategy

## Test Organization

```
backend/tests/                    # Cross-cutting tests
├── architecture/                 # Import + structure enforcement
├── integration/                  # Cross-module integration
└── functional/                   # End-to-end API

modules/<name>/tests/             # Module-specific tests
├── unit/                         # Pure business logic, no DB
├── integration/                  # With DB, single module
└── api/                          # HTTP endpoint tests
```

## What Each Test Type May Use

| Type | May Use | Must Not Use |
| ------ | --------- | -------------- |
| Unit (domain) | Plain Python | Database, HTTP, external services |
| Unit (application) | `@transaction.atomic`, test DB | HTTP, DRF |
| Integration | Django test client | External services (mock) |
| API | DRF test client | Direct model manipulation for assertions |
| Architecture | `ast`, `pathlib`, `importlib` | Production code paths |

## Architecture Tests

- Run without Django: `uv run pytest backend/tests/architecture/ -p no:django`
- Enforce module boundaries via AST import analysis
- Verify structural conventions via filesystem inspection
- Every import-linter contract has a test proving it rejects invalid imports

## Running Tests

```bash
uv run pytest                                              # All tests
uv run pytest backend/tests/architecture/ -p no:django     # Architecture only
uv run pytest backend/src/abren_one/modules/organizations/ # One module
uv run lint-imports                                        # Import contracts
```
