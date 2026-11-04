# Vision — Abren One

## What Is Abren One?

Abren One is an **operating system for NGOs** — a unified platform that manages the full breadth of NGO operations in a single, coherent system.

## The Problem

NGOs operate across programs, finance, fundraising, human resources, procurement, and compliance — typically using disconnected tools, spreadsheets, and manual processes. This fragmentation creates:

- **Data silos** — information trapped in disconnected systems
- **Operational overhead** — staff time spent on reconciliation and manual data transfer
- **Reporting burden** — donor and regulatory reports assembled manually from multiple sources
- **Accountability gaps** — no single source of truth for financial and programmatic data

## The Solution

Abren One provides a single platform where:

- **Organizations** manage their structure — branches, departments, teams, and memberships
- **Programs** define and deliver projects, activities, and their outcomes
- **Finance** (future) records all financial activity with native double-entry accounting
- **Fundraising** (future) tracks donors, grants, and restricted funding
- **HR** (future) manages staff, volunteers, and payroll
- **Procurement** (future) handles purchasing workflows
- **Reporting** (future) generates donor reports, regulatory filings, and management dashboards

All of these capabilities share a common data foundation, common authorization model, and common audit trail.

## Design Principles

1. **Multi-organization from day one** — every feature is tenant-aware. A single deployment serves multiple NGOs.
2. **Domain-driven modules** — each business capability is a self-contained module with clear boundaries. Modules communicate through explicit public interfaces.
3. **Financial integrity** — monetary operations use proper accounting principles. No floating-point currency. No silent rewrites.
4. **Auditability** — every significant action is recorded with who, what, when, and why.
5. **Progressive complexity** — start with core modules (organizations, programs). Add capabilities as they're needed, not before.

## Target Users

- NGO staff managing day-to-day operations
- Program managers overseeing project delivery
- Finance teams tracking budgets and expenditures
- Executive leadership needing cross-cutting visibility
- Donors and regulators requiring accountability reports
