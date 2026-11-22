# Frontend Conventions

> **Status:** Active & Implemented — Vue 3 + TypeScript SPA with Vite, Pinia, and Vue Router.

---

## Technology Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Vue 3 | Latest stable | UI framework |
| TypeScript | Latest stable | Type-safe JavaScript |
| Composition API | — | Component architecture (not Options API) |

## Project Structure

The frontend lives in the `/frontend/` directory with its own `package.json`, independent of the backend Python project.

```
frontend/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── components/
│   ├── views/
│   ├── stores/
│   ├── api/
│   └── types/
└── tests/
```

## API Communication

### Authentication

The frontend uses **Django session authentication with CSRF protection**.

- **No JWT** — the application is a same-origin Vue + Django deployment
- The frontend includes Django's CSRF token in every mutating request
- Session cookies handle authentication state

### Tenant Context

Every tenant-scoped API request must include the `X-Organization-ID` header:

```typescript
const response = await fetch('/api/v1/programs/', {
  headers: {
    'X-Organization-ID': activeOrganizationId,
    'X-CSRFToken': csrfToken,
  },
});
```

### API Contract

The API contract is defined by the **OpenAPI specification** generated from DRF. The frontend consumes this spec — it does not define its own API expectations.

## Conventions (To Be Defined)

The following conventions will be established when frontend implementation begins:

- Component naming and organization
- State management patterns (Pinia)
- Routing conventions (Vue Router)
- Form handling and validation
- Error display and user feedback
- Accessibility implementation (see [Accessibility Standards](accessibility.md))
- Testing strategy (Vitest, Playwright)
- Build and deployment pipeline
- Internationalization (vue-i18n)
