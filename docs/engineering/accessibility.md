# Accessibility Standards

Abren One is designed to serve NGO staff across diverse contexts, including users with disabilities, users on low-bandwidth connections, and users working in multiple languages.

---

## Commitment

Abren One targets **WCAG 2.1 Level AA** conformance for all user-facing interfaces.

## Backend Responsibilities

The backend supports accessible interfaces by providing:

### Structured Error Responses

All API errors return a consistent structure with actionable detail:

```json
{
  "code": "validation_error",
  "message": "Invalid input",
  "details": [
    {
      "field": "amount",
      "code": "invalid",
      "message": "Amount must be a positive number"
    }
  ]
}
```

- Error messages must be human-readable and specific
- Field-level errors reference the exact field name
- Error codes are machine-parseable for frontend translation

### Semantic Field Names

API field names should be self-documenting. Frontends use these names to generate accessible labels and help text.

### Pagination Metadata

List endpoints provide navigation metadata so frontends can build accessible pagination controls:

```json
{
  "results": [...],
  "next_cursor": "...",
  "has_more": true,
  "total_count": 42
}
```

## Frontend Responsibilities (Future)

When the Vue 3 frontend is implemented, it must follow these principles:

- **Semantic HTML** — use proper heading hierarchy, landmarks, lists, and form elements
- **ARIA attributes** — provide roles, labels, and live regions where native semantics are insufficient
- **Keyboard navigation** — all interactive elements must be reachable and operable via keyboard
- **Focus management** — modals, drawers, and dynamic content must manage focus correctly
- **Color contrast** — minimum 4.5:1 for normal text, 3:1 for large text
- **Motion preferences** — respect `prefers-reduced-motion`
- **Screen reader compatibility** — test with VoiceOver (macOS), NVDA (Windows), and TalkBack (Android)

## Internationalization

NGOs operate globally. The architecture supports:

- **Django's i18n framework** for backend message translation
- **UTF-8 everywhere** — database, API, and frontend
- **Date/time formatting** — respect user locale; store in UTC
- **Right-to-left (RTL) support** — planned for Arabic, Hebrew, and other RTL languages
- **Currency display** — format according to locale; store as Decimal with ISO 4217 code

Detailed i18n conventions will be defined when multi-language support is implemented.

## Testing

- API error responses are tested for consistent structure
- Frontend accessibility will be tested with automated tools (axe-core) and manual audits
- Every form endpoint is tested for proper validation error detail
