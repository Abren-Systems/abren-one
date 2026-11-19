# Abren One Infrastructure

## Local PostgreSQL Service

Abren One targets **PostgreSQL 16+** for production deployment. While SQLite is used for fast, zero-dependency unit and architecture test suites, local development and staging environments can run containerized PostgreSQL.

### Starting PostgreSQL

```bash
docker compose -f infra/docker-compose.yml up -d
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
