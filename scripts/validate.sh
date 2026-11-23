#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Abren One — Local Validation Pipeline
# Runs the identical gates executed by CI.
# ==============================================================================

echo "==> 1. Django system check"
uv run python backend/manage.py check --settings=config.settings.test

echo "==> 2. Ruff linter"
uv run ruff check .

echo "==> 3. Ruff format check"
uv run ruff format --check .

echo "==> 4. Pyright type check"
uv run pyright

echo "==> 5. Import linter"
uv run lint-imports

echo "==> 6. Pytest test suite"
uv run pytest

echo "==> 7. Frontend tests"
(cd frontend && pnpm test)

echo "==> 8. Frontend build"
(cd frontend && pnpm run build)

echo "=============================================================================="
echo " All validation gates passed successfully! "
echo "=============================================================================="
