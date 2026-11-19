# Abren One Infrastructure

## Local PostgreSQL Service

Abren One targets **PostgreSQL 18+** (with forward-compatibility for 19+) for development and production deployment. While SQLite in-memory is used for fast, zero-dependency unit and architecture test suites, local development, staging, and production environments utilize containerized PostgreSQL.

### Architecture Note on PostgreSQL 18+

Starting in PostgreSQL 18+, official Docker images structure data under `/var/lib/postgresql` (major-version specific subdirectories) for seamless `pg_upgrade --link` support. The compose service mounts to `/var/lib/postgresql` accordingly.

### Starting PostgreSQL

```bash
docker compose -f infra/docker-compose.yml up -d
```

To specify a custom or development image (e.g. PostgreSQL 19 when available):
```bash
POSTGRES_IMAGE=postgres:19-alpine docker compose -f infra/docker-compose.yml up -d
```

Check service health:
```bash
docker compose -f infra/docker-compose.yml ps
```

### Running Django with PostgreSQL

Enable PostgreSQL in development by setting `USE_POSTGRES=1`:

```bash
# Apply all database migrations to PostgreSQL
USE_POSTGRES=1 uv run python backend/manage.py migrate --settings=config.settings.local

# Run Django system check against PostgreSQL
USE_POSTGRES=1 uv run python backend/manage.py check --settings=config.settings.local

# Start local development server with PostgreSQL
USE_POSTGRES=1 uv run python backend/manage.py runserver --settings=config.settings.local
```

### Stopping PostgreSQL

```bash
# Stop containers
docker compose -f infra/docker-compose.yml down

# Stop containers and remove persisted database volumes
docker compose -f infra/docker-compose.yml down -v
```
