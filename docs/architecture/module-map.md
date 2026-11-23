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
| `finance` | Chart of Accounts, General Ledger, Double-Entry Journal | Ledger accounts, journal entries, balanced financial postings |
| `procurement` | Suppliers, Requisitions, Purchase Orders, Goods Receipt | Vendor directory, spend authorizations, commercial orders, delivery verification |
| `inventory` | Stock Master Data, Immutable Ledger, Balances, Movements | Item categories, durable & consumable items, batch/expiry tracking, multi-warehouse stock balances, transfers, write-offs, intake receipts |

## Future Modules (Not Yet Implemented)

| Module | Responsibility |
|--------|---------------|
| `hr` | Staff records, employment contracts, volunteers, project allocations |
| `reporting` | Donor financial & narrative reporting, budget vs. actuals, analytics |
| `governance` | Organizational controls, compliance, and oversight |
