# Frontend Architecture — Abren One

## 1. Overview & Pattern

Abren One's frontend is a single-page application built with **Vue 3, TypeScript, Pinia, Vue Router, and Vite**, managed via **pnpm**.

To maintain parity with the backend's strict modular monolith principles, the frontend follows a **Domain-Oriented Composable Architecture**:
- Business logic is encapsulated in **Domain Composables**.
- UI rendering is decomposed into **Thin Views**, **Domain Tabs**, **Domain Modals**, and **Common Design System Primitives**.
- API operations are channeled through **Typed API Services** backed by a central client with automated tenant and CSRF header injection.

---

## 2. Directory Structure & Layer Hierarchy

```
frontend/src/
├── api/                  # HTTP communication layer
│   ├── client.ts         # Central fetch wrapper (tenant header, CSRF, typed ApiError)
│   └── modules/          # Strongly typed domain API services (inventory, finance, etc.)
├── assets/               # Global styling, CSS tokens, and theme reset
├── components/           # UI components
│   ├── common/           # Shared design system primitives (ModalDialog, StatusBadge, etc.)
│   └── <module>/         # Module-specific UI components
│       ├── tabs/         # Tab panel views (e.g. StockBalancesTab.vue)
│       └── modals/       # Specialized modal forms (e.g. CreateItemModal.vue)
├── composables/          # Domain state & workflow logic (useInventory, useProcurement)
├── router/               # Route definitions and navigation guards (auth & tenancy)
├── stores/               # Application-level singleton stores (auth, tenant context)
├── types/                # Strongly-typed TypeScript interfaces & DTOs
└── views/                # Route target views — thin orchestrators (<200 LOC)
```

### Dependency Direction

```
Views (Route entrypoints, page headers, tab navigation)
  │
  ├──▶ Composables (Domain reactive state, actions, loading, error handling)
  │      │
  │      └──▶ API Services (Endpoints, payload serialization, error mapping)
  │             │
  │             └──▶ API Client (Fetch, tenant context, CSRF, response parsing)
  │
  └──▶ Components
         ├──▶ Common Primitives (ModalDialog, StatusBadge, EmptyState)
         └──▶ Domain Tabs & Modals (Form controls, data tables, emitted events)
```

---

## 3. Layer Responsibilities & Rules

### 3.1 Views (`src/views/`)
- **Role:** Thin orchestrators.
- **Rules:**
  - Must remain under ~200 lines of code.
  - Must not declare inline modal markup or raw `fetch`/`api.get` calls.
  - Wire up composables, manage current active tab, and pass props/listeners to tab and modal components.

### 3.2 Composables (`src/composables/`)
- **Role:** Stateful business logic per domain.
- **Rules:**
  - Own reactive variables (`items`, `balances`, `isLoading`, `errorMessage`).
  - Provide domain mutation actions (`loadData`, `createItem`, `recordMovement`).
  - Automatically react to active tenant changes from `useTenantStore()`.
  - Encapsulate try/catch blocks and user notification triggers.
  - Easily unit testable with Vitest without mounting virtual DOM.

### 3.3 Common Design System Primitives (`src/components/common/`)
- **Role:** Headless or styled reusable UI primitives.
- **Rules:**
  - Follow modern web standards:
    - `ModalDialog.vue`: Uses native `<dialog>` element, `overscroll-behavior: contain`, `aria-labelledby`, Esc dismissal, and focus management.
    - `StatusBadge.vue`: Type-safe status pill supporting all NGO lifecycle states.
    - `EmptyState.vue`: Consistent zero-state UI with optional action slot.
    - `LoadingSpinner.vue`: Consistent loading indicator.

### 3.4 Domain Components (`src/components/<module>/`)
- **Role:** Tab panels, complex forms, and workflow modals.
- **Rules:**
  - Co-located by domain (`inventory/`, `procurement/`, `finance/`, etc.).
  - Split into `tabs/` (data tables, filter bars, action toolbars) and `modals/` (create, edit, intake workflows).
  - Communicate with parents via explicit typed Vue `defineProps` and `defineEmits`.

### 3.5 Global Stores (`src/stores/`)
- **Role:** Application-wide session singletons only.
- **Rules:**
  - Limited to `useAuthStore` (user identity, login/logout, tokens) and `useTenantStore` (active organization, available memberships).
  - Domain records (items, POs, journal entries) belong in domain composables, not global stores.

---

## 4. Modern Web Standards & Best Practices

1. **Dialogs & Overlays:**
   - Modals use the native `<dialog>` element with `showModal()` and top-layer management.
   - Background page scroll is contained via `overscroll-behavior: contain` on `:modal` and `::backdrop`.
   - Accessible names are required using `aria-labelledby` pointing to the modal title.
2. **Data Tables:**
   - Standard semantic `<table>`, `<thead>`, `<tbody>`, `<th>`, `<td>`.
   - Wrapped in responsive scroll containers with sticky headers where appropriate.
3. **Typography & Styling:**
   - CSS tokens via standard custom properties (`--color-primary`, `--radius-md`, `--shadow-sm`).
   - Scoped styles in SFCs, utilizing global utility classes for layout (`.card`, `.btn`, `.form-input`).

---

## 5. Testing Strategy

1. **API Client & Services:** Unit test header injection, CSRF handling, 4xx/5xx `ApiError` conversion.
2. **Stores:** Test tenant selection, localStorage synchronization, and header syncing.
3. **Composables:** Test reactive lifecycle, loading states, and data fetching actions.
4. **Components:** Test accessibility labels, slot rendering, and emitted event payloads.
