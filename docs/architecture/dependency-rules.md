# Dependency Rules

## Cross-Module Rules

| Interaction | Permitted | Prohibited |
| ------------- | ----------- | ------------ |
| Module reads another module's published query | ✅ Via `public.py` | |
| Module calls another module's published command | ✅ Via `public.py` | |
| Module imports another module's internal model | | ❌ |
| Module writes to another module's tables | | ❌ |
| Module imports another module's private services | | ❌ |
| Platform depends on a business module | | ❌ |
| Business module depends on platform | ✅ | |
| Django ORM ForeignKey to another module's model | ✅ String reference, documented | |

## Public Interface Convention

Every business module exposes capabilities through `public.py`:

- Application queries and commands
- Result DTOs
- Domain exceptions callers must handle
- **Not** ORM model classes (use string-based FK references instead)

## Enforcement

- **import-linter**: Broad structural rules (platform ↛ modules, layer direction)
- **Architecture pytest tests**: Cross-module `public.py` enforcement via AST analysis
- Both run in CI as mandatory gates
