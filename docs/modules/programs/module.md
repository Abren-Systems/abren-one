# Programs Module

**App label:** `programs`
**Location:** `backend/src/abren_one/modules/programs/`
**Status:** Planned — implementation in Stage 3

---

## Purpose

Manages program delivery — Program, Project, and Activity definition and operational delivery. This module represents the core service-delivery domain of the NGO, structuring work into a hierarchy of long-running initiatives, time-bound projects, and specific activities.

## Owned Models

> To be implemented in Stage 3.

| Model | Description |
|-------|-------------|
| `Program` | A long-running initiative that groups related projects under a strategic objective. |
| `Project` | A time-bound effort with defined deliverables, belonging to a program. |
| `Activity` | A specific task or action within a project. |

All models use UUID primary keys and include `created_at` / `updated_at` timestamps per the architecture conventions (§4.1). All records are tenant-scoped (organization-owned).

## Public Interface

**File:** `public.py`

Other modules import **only** from this file.

### Planned Exports (Stage 3)

| Export | Type | Description |
|--------|------|-------------|
| `list_programs` | Query | List programs for the active organization. Returns a list of `ProgramSummaryResult`. |
| `get_program` | Query | Retrieve a specific program by ID. Returns `ProgramDetailResult`. |
| `ProgramSummaryResult` | DTO | Frozen dataclass with `id`, `name`, `status`, `organization_id`. |
| `ProgramDetailResult` | DTO | Frozen dataclass with full program details including project count. |

```python
# Example public.py (Stage 3)
from abren_one.modules.programs.application.queries.list_programs import (
    list_programs,
    ProgramSummaryResult,
)
from abren_one.modules.programs.application.queries.get_program import (
    get_program,
    ProgramDetailResult,
)

__all__ = [
    "list_programs",
    "ProgramSummaryResult",
    "get_program",
    "ProgramDetailResult",
]
```

## Cross-Module Dependencies

### This Module Depends On

| Module | How It Depends | Mechanism |
|--------|---------------|-----------|
| **Organizations** | Reads org context; all records scoped to an Organization | `public.py` queries + string FK `"organizations.Organization"` |
| `platform/identity` | Platform | User model for activity assignments and audit context |
| `platform/common` | Platform | `ExecutionContext`, `TimestampMixin`, `OrgOwnedMixin`, typed exceptions |

### Inbound ForeignKeys to Organizations

All tenant-scoped models in this module reference Organization via string FK:

```python
# In Program model
organization = models.ForeignKey(
    "organizations.Organization",
    on_delete=models.PROTECT,
    related_name="+",
)
```

Or by inheriting from `OrgOwnedMixin` (provided by `platform/common/models.py`), which supplies the same field.

### Future Cross-Module Consumers

As the system grows, modules such as Finance (budget tracking per program/project) may consume this module's public interface. Those dependencies will be documented when they are implemented.

## Key Domain Concepts

### Program

- A **long-running initiative** that groups related projects under a shared strategic objective.
- Programs have a lifecycle (e.g., planning, active, completed, archived).
- A program belongs to exactly one organization.

### Project

- A **time-bound effort** with defined start/end dates and deliverables.
- Projects belong to exactly one program.
- Projects track progress toward their deliverables.

### Activity

- A **specific task** within a project.
- Activities are the most granular unit of work tracked by this module.
- Activities may be assigned to organization members.

### Tenant Scoping

- All records are organization-owned — every query must be scoped to the active organization context.
- Cross-tenant access is denied; records belonging to a different organization return 404 (§5.4).
- The `ExecutionContext.organization_id` is required and verified for all operations.

## Boundary — What This Module Does NOT Own

| Concept | Owned By |
|---------|----------|
| Organizational structure (orgs, branches, departments) | `modules/organizations` |
| Membership and roles | `modules/organizations` |
| Financial tracking (budgets, expenditures) | Future `modules/finance` |
| User accounts and authentication | `platform/identity` |
| Tenant resolution | `platform/tenancy` |
| Permission evaluation | `platform/authorization` |
| Audit event persistence | `platform/audit` |

## Internal Structure (Target — Stage 3)

```
modules/programs/
├── __init__.py
├── apps.py
├── admin.py
├── public.py
├── AGENTS.md
├── README.md
│
├── models/
│   ├── __init__.py
│   ├── program.py
│   ├── project.py
│   └── activity.py
│
├── domain/
│   ├── __init__.py
│   ├── policies.py          # Program lifecycle rules, project eligibility
│   ├── exceptions.py        # Domain-specific exceptions
│   └── value_objects.py     # Status enums, delivery types
│
├── application/
│   ├── commands/
│   │   ├── create_program.py
│   │   ├── update_program.py
│   │   ├── create_project.py
│   │   ├── update_project.py
│   │   ├── create_activity.py
│   │   └── update_activity.py
│   └── queries/
│       ├── list_programs.py
│       ├── get_program.py
│       ├── list_projects.py
│       └── list_activities.py
│
├── interfaces/
│   └── api/
│       └── v1/
│           ├── urls.py
│           ├── views.py
│           ├── serializers.py
│           └── permissions.py
│
├── migrations/
│
└── tests/
    ├── unit/
    ├── integration/
    └── api/
```

## Stage 3 Deliverables

1. **Models:** `Program`, `Project`, `Activity` with full field definitions, constraints, indexes, and organization FK.
2. **Commands:** `create_program`, `update_program`, `create_project`, `update_project`, `create_activity`, `update_activity` — each with `@transaction.atomic`, `ExecutionContext`, frozen input/output dataclasses.
3. **Queries:** `list_programs`, `get_program`, `list_projects`, `list_activities` — returning DTOs, tenant-scoped.
4. **Public interface:** `public.py` exposing queries and DTOs for future cross-module consumers.
5. **API endpoints:** RESTful endpoints under `/api/v1/programs/` with DRF views, serializers, and permissions.
6. **Admin registration:** Django admin for all models.
7. **Cross-module interaction test:** Verify that Programs correctly reads organization context via the Organizations module's `public.py` — confirming the cross-module boundary contract works end-to-end.
8. **Tests:**
   - Unit tests for domain policies (lifecycle transitions, eligibility rules).
   - Integration tests for commands and queries (with DB).
   - API tests for all endpoints (including negative cross-tenant tests per §5.6).
   - Architecture tests confirming module boundary compliance.

## Architectural References

- Module classification and dependency direction: Architecture Contracts §2
- Public interface rules: Architecture Contracts §3
- ORM model conventions: Architecture Contracts §4
- Tenant and organization context: Architecture Contracts §5
- Command/query conventions: Architecture Contracts §6
- API boundary conventions: Architecture Contracts §7
- Authorization and audit: Architecture Contracts §8
