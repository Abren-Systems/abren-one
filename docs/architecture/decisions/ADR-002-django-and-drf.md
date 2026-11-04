# ADR-002: Django 6.1 + DRF 3.18

**Status:** Accepted
**Date:** 2026-11-04

## Context

We need a web framework that provides ORM, migrations, authentication, admin, and API capabilities. Python 3.15 is our runtime.

## Decision

Use Django 6.1.3 (first release supporting Python 3.15) with Django REST Framework 3.18.3. Use Django's ORM pragmatically — application code uses models directly without mandatory repository abstractions.

## Consequences

- Django's productive ORM, migrations, and auth infrastructure are available
- DRF provides API serialization, permissions, and OpenAPI generation
- Domain rules remain independent of Django ORM queries and HTTP
- We use Django's capabilities rather than abstracting them away
- Django 6.1 mainstream support ends April 2027; track upgrade path
