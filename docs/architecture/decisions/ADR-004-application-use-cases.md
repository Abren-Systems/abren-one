# ADR-004: Application Use Cases (Commands and Queries)

**Status:** Accepted
**Date:** 2026-11-04

## Context

Business logic scattered across views, serializers, and signals becomes untestable and hard to trace. We need a consistent pattern for business operations.

## Decision

- Every state-changing operation has an explicit command in `application/commands/`
- Every significant read operation has a query in `application/queries/`
- Commands receive an `ExecutionContext` with verified actor and tenant identity
- Commands use `@transaction.atomic` for explicit transaction boundaries
- DRF views delegate to commands/queries — they do not contain business logic

## Consequences

- Operations are traceable from API endpoint to business logic to persistence
- Business rules can be tested without HTTP
- Commands can be called from API, scheduled jobs, or other commands
- The pattern is repeatable for AI agents
