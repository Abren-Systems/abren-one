# Data Ownership

## Model Conventions

All **application-owned** business and platform records follow these defaults. Exceptions require documented justification.

| Convention | Default | Notes |
|------------|---------|-------|
| UUID primary key | All application records | `models.UUIDField(primary_key=True, default=uuid.uuid4)` |
| `created_at` | Where meaningful | `auto_now_add=True` |
| `updated_at` | Models that change | `auto_now=True` — not an audit history |
| Organization FK | Org-scoped records | Explicit, not implicit |
| Soft deletion | Only with justification | Not a universal default |

## Ownership Rules

- Every model belongs to exactly one module
- Only the owning module creates migrations for its models
- Cross-module ForeignKeys use string references and are documented in both modules
- No module adds fields to another module's models
- Monetary values: `DecimalField`, never `FloatField`

## Optional Mixins (`platform/common/`)

- `TimestampMixin` — `created_at` + `updated_at`
- `OrgOwnedMixin` — organization FK with `PROTECT`

These are opt-in. Modules may define fields directly when the mixin doesn't fit.
