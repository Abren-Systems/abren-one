# Domain Glossary

Key domain terms used throughout Abren One.

## Organizational Concepts

| Term | Definition |
| ------ | ----------- |
| **Organization** | A registered NGO or entity that operates as a tenant within Abren One. The top-level boundary for data isolation. |
| **Branch** | A geographic or operational subdivision of an organization. |
| **Department** | A functional subdivision within a branch (e.g., Finance, Programs). |
| **Membership** | The relationship between a user and an organization, including status (active, suspended, revoked) and role. |
| **Tenant** | Synonymous with Organization in a data-isolation context. Every tenant-scoped record belongs to exactly one organization. |

## Program Concepts

| Term | Definition |
| ------ | ----------- |
| **Program** | A long-running initiative that groups related projects toward a common goal. |
| **Project** | A time-bound effort within a program, with defined deliverables and resources. |
| **Activity** | A specific task or work item within a project. |

## Identity & Access

| Term | Definition |
| ------ | ----------- |
| **User** | A global identity in the system. A user can belong to multiple organizations. |
| **Actor** | The entity performing an operation — may be a user, system process, integration, or administrator. |
| **ExecutionContext** | A trusted dataclass carrying the verified actor identity, organization context, and correlation ID for a business operation. |
| **Active organization** | The organization a user has selected as their working context for the current session/request. |

## Architecture Terms

| Term | Definition |
| ------ | ----------- |
| **Module** | A self-contained business capability (e.g., organizations, programs, fundraising). |
| **Platform** | Cross-cutting infrastructure capabilities shared across modules (identity, tenancy, authorization, audit, common). |
| **Integration** | An adapter connecting Abren One to an external system. |
| **public.py** | The single file through which a module exposes capabilities to other modules. |
| **Command** | A state-changing application operation. |
| **Query** | A read-only application operation. |
| **DTO** | Data Transfer Object — a frozen dataclass used to pass data across boundaries without leaking model internals. |

## Financial Concepts (Future)

| Term | Definition |
| ------ | ----------- |
| **Journal Entry** | A balanced, immutable record of a financial transaction (debits equal credits). |
| **Restricted Funding** | Donor funds that must be spent on a specific purpose or project. |
| **Chart of Accounts** | The structured list of accounts used to classify financial transactions. |
| **Reversal Entry** | A corrective journal entry that offsets an erroneous posted entry — posted entries are never silently rewritten. |
