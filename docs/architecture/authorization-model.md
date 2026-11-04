# Authorization Model

## Six Authorization Layers

| Layer | Question | Where Enforced |
|-------|----------|----------------|
| **Authentication** | Who is the caller? | `platform/identity` + DRF session auth |
| **Tenant membership** | Does the user belong to this org? | `platform/tenancy` |
| **Role/permission** | Is this action type allowed? | `platform/authorization` |
| **Business eligibility** | Is the record in a valid state? | Module application layer |
| **Approval** | Has the required decision been made? | Module application layer |
| **Segregation of duties** | Is this action combination permitted? | Module application layer |

## Tenancy: Five Security Invariants

Applied according to the operation's nature — not a rigid identical sequence:

1. **Authenticated** — caller has valid identity
2. **Organization valid** — active org context resolved
3. **Membership active** — user has active membership
4. **Record ownership** — target belongs to active org
5. **Operation authorized** — user has permission

## Context Resolution Sequence

1. Django session authentication establishes identity
2. `X-Organization-ID` header provides requested org context
3. Server verifies active membership on every request
4. Application command receives `ExecutionContext` with verified identity

## ExecutionContext

```python
@dataclass(frozen=True)
class ExecutionContext:
    actor_type: ActorType  # user, system, integration, administrator
    actor_id: UUID | None
    organization_id: UUID | None
    correlation_id: UUID
```

## Fail-Closed Rules

| Condition | Behavior |
|-----------|----------|
| No org context on tenant-scoped query | **Deny** |
| User has no membership in requested org | **Deny** |
| Record belongs to different org | **404** (do not reveal existence) |
| Background job without org context | **Fail** |
| Admin/superuser bypass | **Explicit and audited** |
