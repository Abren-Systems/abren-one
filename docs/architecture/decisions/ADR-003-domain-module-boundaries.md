# ADR-003: Domain Module Boundaries

**Status:** Accepted
**Date:** 2026-11-04

## Context

Django apps are framework concepts. Our business modules are architectural concepts. Without explicit boundary rules, modules become interconnected and ownership erodes.

## Decision

- One Django app per meaningful domain module
- Cross-module imports only through `public.py`
- ForeignKeys to other modules use string references
- Platform modules cannot depend on business modules
- Boundaries enforced by import-linter + architecture tests

## Consequences

- Modules can be understood and worked on independently
- AI agents can work on one module without understanding the entire system
- New modules follow the same pattern
- Module ownership is testable and enforced
