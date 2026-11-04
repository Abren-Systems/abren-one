# ADR-001: Modular Monolith Architecture

**Status:** Accepted
**Date:** 2026-11-04

## Context

Abren One is an NGO operating system spanning multiple business domains (organizations, programs, finance, procurement, inventory, beneficiaries). We need an architecture that supports independent domain ownership without the operational complexity of microservices.

## Decision

Adopt a domain-oriented modular monolith with explicit module boundaries, enforced by import-linter contracts and architecture tests.

## Consequences

- Each business capability has an identifiable owner module
- Cross-module communication uses published interfaces (`public.py`)
- Module boundaries are enforced automatically, not by convention alone
- The system can be decomposed later if genuinely needed
- All modules share one deployment unit, database, and transaction context
