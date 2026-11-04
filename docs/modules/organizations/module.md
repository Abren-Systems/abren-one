# Organizations Module

**App label:** `organizations`
**Location:** `backend/src/abren_one/modules/organizations/`
**Status:** Scaffold (Stage 1) — full implementation in Stage 2

---

## Purpose

Manages organizational structure — Organization, Branch, Department, and Membership records and workflows. This is the foundational business module that all tenant-scoped modules depend on for organizational context.

## Owned Models

> To be implemented in Stage 2.

| Model | Description |
| ------- | ------------- |
| `Organization` | Top-level tenant entity. All tenant-scoped records ultimately belong to an organization. |
| `Branch` | Physical or logical subdivision of an organization (e.g., regional office). |
| `Department` | Functional grouping within an organization or branch. |
| `Membership` | Connects a User (from `platform/identity`) to an Organization with role and status. |

All models use UUID primary keys and include `created_at` / `updated_at` timestamps per the architecture conventions (§4.1).

## Public Interface

**File:** `public.py`

Other modules import **only** from this file. Cross-module ForeignKeys use string references (`"organizations.Organization"`), not direct model imports.

### Planned Exports (Stage 2)

| Export | Type | Description |
| -------- | ------ | ------------- |
| `get_organization` | Query | Retrieve an organization by ID. Returns `GetOrganizationResult`. |
| `GetOrganizationResult` | DTO | Frozen dataclass with `id`, `name`, `slug`, `is_active`. |
| `get_user_membership` | Query | Look up a user's membership in a specific organization. Returns `MembershipResult`. |
| `MembershipResult` | DTO | Frozen dataclass with membership status, role, and branch access details. |

```python
# Example public.py (Stage 2)
from abren_one.modules.organizations.application.queries.get_organization import (
    get_organization,
    GetOrganizationResult,
)
from abren_one.modules.organizations.application.queries.get_membership import (
    get_user_membership,
    MembershipResult,
)

__all__ = [
    "get_organization",
    "GetOrganizationResult",
    "get_user_membership",
    "MembershipResult",
]
```

## Cross-Module Relationships

### Consumers (modules that depend on Organizations)

| Module | How It Depends | Mechanism |
| -------- | --------------- | ----------- |
| **Programs** | Reads org context; FK to `Organization` | `public.py` queries + string FK `"organizations.Organization"` |
| **Tenancy** (platform) | Resolves active org context, verifies membership | `public.py` queries |
| **Authorization** (platform) | Reads membership roles for permission evaluation | `public.py` queries |

### Inbound Cross-Module ForeignKeys

Other modules reference Organization via string FK:

```python
# In another module's model
organization = models.ForeignKey(
    "organizations.Organization",
    on_delete=models.PROTECT,
    related_name="+",
)
```

This is the canonical pattern. The `OrgOwnedMixin` in `platform/common/models.py` provides this field for tenant-scoped records.

## Key Domain Concepts

### Organization Lifecycle

```
Provisioning → Active → Suspended → (Reactivated | Archived)
```

- **Provisioning** is an explicit, secure path — no pre-existing organization context is required (tenancy invariants 1 and 5 only; see §5.3).
- **Activation** enables normal operations.
- **Suspension** freezes all operations while preserving data.

### Membership Lifecycle

```
Invitation → Active → Suspended → Revoked
                ↑         │
                └─────────┘  (Reactivation)
```

- **Invitation:** A user is invited to join an organization.
- **Activation:** The membership becomes effective; the user can operate within the organization.
- **Suspension:** Temporarily disables access without revoking the relationship.
- **Revocation:** Permanently ends the membership.

### Branch / Department Structure

- Branches are subdivisions of an Organization (physical or logical).
- Departments are functional groupings within an Organization or Branch.
- Branch access is part of the membership context, enforced by the Organizations module with support from the Authorization platform.

### Representative Role Management

- Organization members may hold representative roles.
- Role assignment and management is owned by this module.
- Permission evaluation based on roles is delegated to `platform/authorization`.

## Dependencies

| Dependency | Type | What Is Used |
|------------|------|--------------|
| `platform/identity` | Platform | `User` model — the global identity that memberships connect to organizations |
| `platform/common` | Platform | `ExecutionContext`, `TimestampMixin`, `OrgOwnedMixin`, typed exceptions |

## Boundary — What This Module Does NOT Own

| Concept | Owned By |
| --------- | ---------- |
| User accounts and authentication | `platform/identity` |
| Tenant resolution (active org context) | `platform/tenancy` |
| Permission evaluation (role → allowed actions) | `platform/authorization` |
| Audit event persistence | `platform/audit` |
| Program/project/activity records | `modules/programs` |

## Internal Structure (Target — Stage 2)

``` txt
modules/organizations/
├── __init__.py
├── apps.py
├── admin.py
├── public.py
├── AGENTS.md
├── README.md
│
├── models/
│   ├── __init__.py
│   ├── organization.py
│   ├── branch.py
│   ├── department.py
│   └── membership.py
│
├── domain/
│   ├── __init__.py
│   ├── policies.py          # Membership eligibility, org lifecycle rules
│   ├── exceptions.py        # Domain-specific exceptions
│   └── value_objects.py     # Status enums, role types
│
├── application/
│   ├── commands/
│   │   ├── create_organization.py
│   │   ├── create_branch.py
│   │   ├── create_department.py
│   │   ├── invite_member.py
│   │   ├── activate_membership.py
│   │   ├── suspend_membership.py
│   │   └── revoke_membership.py
│   └── queries/
│       ├── get_organization.py
│       ├── get_membership.py
│       ├── list_branches.py
│       └── list_members.py
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

## Stage 2 Deliverables

1. **Models:** `Organization`, `Branch`, `Department`, `Membership` with full field definitions, constraints, and indexes.
2. **Commands:** `create_organization`, `create_branch`, `create_department`, `invite_member`, `activate_membership`, `suspend_membership`, `revoke_membership` — each with `@transaction.atomic`, `ExecutionContext`, frozen input/output dataclasses.
3. **Queries:** `get_organization`, `get_user_membership`, `list_branches`, `list_members` — returning DTOs, tenant-scoped.
4. **Public interface:** `public.py` exposing queries and DTOs for cross-module consumers.
5. **API endpoints:** RESTful endpoints under `/api/v1/organizations/` with DRF views, serializers, and permissions.
6. **Admin registration:** Django admin for all models.
7. **Tests:**
   - Unit tests for domain policies (membership eligibility, lifecycle transitions).
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
