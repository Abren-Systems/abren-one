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

## Cross-Module Operational Bridges (ADR-006)

Inter-module workflows coordinate business processes across module boundaries exclusively through `public.py` interfaces:

| Bridge | Trigger Operation | Action & Accounting Postings | Failure Strategy |
|--------|-------------------|------------------------------|------------------|
| **Inventory $\to$ Finance** | `receive_purchased_stock` | Dr 1200 Inventory Asset / Cr 2010 AP Clearing | Graceful degradation (skipped if CoA unconfigured) |
| **Inventory $\to$ Finance** | `issue_stock` (program) | Dr 5100 Program Relief Exp / Cr 1200 Inventory Asset | Graceful degradation |
| **Inventory $\to$ Finance** | `issue_stock` (general) | Dr 5000 General Operations Exp / Cr 1200 Inventory Asset | Graceful degradation |
| **Inventory $\to$ Finance** | `write_off_stock` | Dr 5800 Inventory Shrinkage & Loss / Cr 1200 Inventory Asset | Graceful degradation |
| **Inventory $\to$ Finance** | `receive_in_kind_donation` | Dr 1200 Inventory Asset / Cr 3200 In-Kind Revenue | Graceful degradation |
| **Fundraising $\to$ Finance** | `record_donation` | Dr 1010 Bank / Cr 3100 Restricted Grant Revenue | Graceful degradation |
| **Beneficiaries $\to$ Inventory** | `record_service_delivery` | `issue_stock` (batch/expiry checked, stock balance decremented, Auto-GL Dr 5100 / Cr 1200) | Atomic failure (rejects expired batch or insufficient stock) |

## Future Modules (Not Yet Implemented)

| Module | Responsibility |
|--------|---------------|
| `hr` | Staff records, employment contracts, volunteers, project allocations |
| `reporting` | Donor financial & narrative reporting, budget vs. actuals, analytics |
| `governance` | Organizational controls, compliance, and oversight |
