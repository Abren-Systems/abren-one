# Architecture Overview

## Pattern: Domain-Oriented Modular Monolith

Abren One combines three complementary approaches:

1. **Modular Monolith** — organizes around independently owned business domains
2. **Layered Architecture** — separates interface, application, domain, and persistence
3. **Vertical Slices** — organizes operations around business use cases

### Dependency Direction

```
Interfaces (DRF views, serializers, API permissions, Admin)
    │
    ▼
Application (Commands, queries, orchestration, transaction boundaries)
    │
    ├──▶ Domain (Business rules, policies, value objects, domain events)
    │
    └──▶ Module-owned persistence & adapters (Django ORM models, DB access)
```

- Application coordinates domain rules **and** persistence directly
- Domain rules do not depend on DRF, HTTP, or Django ORM queries
- ORM models are owned by their business module
- No mandatory repository abstraction — use Django ORM directly in application layer

### Three Module Categories

| Category | Location | Purpose |
|----------|----------|---------|
| **Platform** | `platform/` | Cross-cutting infrastructure (identity, tenancy, auth, audit) |
| **Modules** | `modules/` | Business domain capabilities (organizations, programs, etc.) |
| **Integrations** | `integrations/` | External system adapters |

### Key Principles

- Every business capability has an identifiable owner
- Every state-changing operation has an explicit use case
- Every module has a defined boundary
- Every dependency has a reason
- Every implementation follows a recognizable pattern

See [dependency-rules.md](dependency-rules.md) for enforcement details.
See [module-map.md](module-map.md) for the complete module inventory.
