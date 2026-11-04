# Module Map

## Platform Modules

| Module | Responsibility | Does NOT Own |
|--------|---------------|--------------|
| `identity` | User accounts, authentication, custom user model | Organization structure |
| `tenancy` | Resolving active org context, enforcing tenant-scoped access | Organization records |
| `authorization` | Roles, permissions, policy evaluation | Business eligibility |
| `audit` | Recording auditable actions | Application logging |
| `common` | Shared base mixins, typed exceptions, ExecutionContext | Must have justification |

## Business Modules (Initial)

| Module | Responsibility | Owns |
|--------|---------------|------|
| `organizations` | Organization, Branch, Department, Membership | Organizational structure and lifecycle |
| `programs` | Program, Project, Activity | Program structure and delivery |

## Future Modules (Not Yet Implemented)

| Module | Responsibility |
|--------|---------------|
| `beneficiaries` | Beneficiary records and support relationships |
| `fundraising` | Donations, donors, grants |
| `finance` | Accounting, budgets, financial controls |
| `procurement` | Purchasing lifecycle |
| `inventory` | Stock, storage, distributions |
| `governance` | Organizational controls and oversight |
