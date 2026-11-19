# Module Map

## Platform Modules

| Module | Responsibility | Does NOT Own |
|--------|---------------|--------------|
| `identity` | User accounts, authentication, custom user model | Organization structure |
| `tenancy` | Resolving active org context, enforcing tenant-scoped access | Organization records |
| `authorization` | Roles, permissions, policy evaluation | Business eligibility |
| `audit` | Recording auditable actions | Application logging |
| `common` | Shared base mixins, typed exceptions, ExecutionContext | Must have justification |

## Business Modules

| Module | Responsibility | Owns |
|--------|---------------|------|
| `organizations` | Organization, Branch, Department, Membership | Organizational structure and lifecycle |
| `programs` | Program, Project, Activity | Program structure and delivery |
| `fundraising` | Donor, Grant, Donation | Funding streams, donors, and contributions |
| `beneficiaries` | Beneficiary, ServiceDelivery | Beneficiary profiles and service delivery tracking |

## Future Modules (Not Yet Implemented)

| Module | Responsibility |
|--------|---------------|
| `finance` | Accounting, budgets, financial controls |
| `procurement` | Purchasing lifecycle |
| `inventory` | Stock, storage, distributions |
| `governance` | Organizational controls and oversight |
