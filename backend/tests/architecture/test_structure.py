"""
Architecture enforcement — module structural convention tests.

These tests use filesystem inspection (``pathlib``) to verify that every
module under ``platform/`` and ``modules/`` follows the structural
conventions defined in the Stage 0 Architecture Contracts (§9.3,
Appendix A).

No Django runtime or database is required.

Rules enforced
--------------
1. Every module under ``platform/`` and ``modules/`` has ``__init__.py``
   and ``apps.py``.
2. Every business module has a ``public.py`` file.
3. Every module has a ``models/`` directory or ``models.py``.
4. Every module has a ``tests/`` directory.
5. Model packages (``models/``) have an ``__init__.py`` that imports
   model classes.
6. Application directories have ``commands/`` and/or ``queries/``
   subdirectories (when ``application/`` exists).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.architecture.conftest import (
    MODULES_ROOT,
    PLATFORM_ROOT,
    ViolationCollector,
    discover_modules,
)

# ── Helpers ────────────────────────────────────────────────────────────────


def _all_registered_modules() -> list[tuple[str, Path]]:
    """Return ``(category, path)`` for every module in platform/ and modules/.

    The category is ``"platform"`` or ``"modules"`` for readable messages.
    """
    result: list[tuple[str, Path]] = []
    for category, root in [("platform", PLATFORM_ROOT), ("modules", MODULES_ROOT)]:
        for d in discover_modules(root):
            result.append((category, d))
    return result


def _module_label(category: str, module_dir: Path) -> str:
    return f"{category}/{module_dir.name}"


# ═══════════════════════════════════════════════════════════════════════════
# Rule 1 — Every module has __init__.py and apps.py  (§9.3, Appendix A)
# ═══════════════════════════════════════════════════════════════════════════


class TestModuleRequiredFiles:
    """Every Python-package module must contain ``__init__.py`` and
    ``apps.py`` so Django can discover and register it.
    """

    @pytest.fixture
    def all_modules(self) -> list[tuple[str, Path]]:
        return _all_registered_modules()

    def test_init_py_exists(self, all_modules: list[tuple[str, Path]]) -> None:
        collector = ViolationCollector()
        for category, module_dir in all_modules:
            init_file = module_dir / "__init__.py"
            if not init_file.exists():
                collector.add(
                    rule="module-init-py",
                    message=(
                        f"`{_module_label(category, module_dir)}` is missing "
                        f"`__init__.py` — every module must be a Python "
                        f"package (§9.3, Appendix A)."
                    ),
                    filepath=module_dir,
                    lineno=0,
                )
        collector.assert_clean("Modules missing __init__.py")

    def test_apps_py_exists(self, all_modules: list[tuple[str, Path]]) -> None:
        collector = ViolationCollector()
        for category, module_dir in all_modules:
            apps_file = module_dir / "apps.py"
            if not apps_file.exists():
                collector.add(
                    rule="module-apps-py",
                    message=(
                        f"`{_module_label(category, module_dir)}` is missing "
                        f"`apps.py` — every module needs a Django AppConfig "
                        f"(§9.3, Appendix A)."
                    ),
                    filepath=module_dir,
                    lineno=0,
                )
        collector.assert_clean("Modules missing apps.py")


# ═══════════════════════════════════════════════════════════════════════════
# Rule 2 — Business modules have public.py  (§3.1, §9.3)
# ═══════════════════════════════════════════════════════════════════════════


class TestBusinessModulesHavePublicPy:
    """Every module under ``modules/`` must have a ``public.py`` that
    defines the cross-module interface.
    """

    def test_public_py_exists(self, modules_root: Path) -> None:
        collector = ViolationCollector()
        for module_dir in discover_modules(modules_root):
            public_file = module_dir / "public.py"
            if not public_file.exists():
                collector.add(
                    rule="module-public-py",
                    message=(
                        f"`modules/{module_dir.name}` is missing `public.py` "
                        f"— every business module must expose its cross-module "
                        f"interface through public.py (§3.1)."
                    ),
                    filepath=module_dir,
                    lineno=0,
                )
        collector.assert_clean("Business modules missing public.py")


# ═══════════════════════════════════════════════════════════════════════════
# Rule 3 — Every module has models/ or models.py  (§4.3, §9.3)
# ═══════════════════════════════════════════════════════════════════════════


class TestModulesHaveModels:
    """Each module must declare its model layer — either as a
    ``models/`` package or a ``models.py`` file.
    """

    @pytest.fixture
    def all_modules(self) -> list[tuple[str, Path]]:
        return _all_registered_modules()

    def test_models_exist(self, all_modules: list[tuple[str, Path]]) -> None:
        collector = ViolationCollector()
        for category, module_dir in all_modules:
            has_models_dir = (module_dir / "models").is_dir()
            has_models_py = (module_dir / "models.py").is_file()
            if not has_models_dir and not has_models_py:
                collector.add(
                    rule="module-models",
                    message=(
                        f"`{_module_label(category, module_dir)}` has neither "
                        f"`models/` directory nor `models.py` — every module "
                        f"must declare its data layer (§4.3, §9.3)."
                    ),
                    filepath=module_dir,
                    lineno=0,
                )
        collector.assert_clean("Modules missing models/ or models.py")


# ═══════════════════════════════════════════════════════════════════════════
# Rule 4 — Every module has tests/  (§9.1, §9.3)
# ═══════════════════════════════════════════════════════════════════════════


class TestModulesHaveTests:
    """Each module must have a ``tests/`` directory for its unit,
    integration, and API tests.
    """

    @pytest.fixture
    def all_modules(self) -> list[tuple[str, Path]]:
        return _all_registered_modules()

    def test_tests_directory_exists(self, all_modules: list[tuple[str, Path]]) -> None:
        collector = ViolationCollector()
        for category, module_dir in all_modules:
            tests_dir = module_dir / "tests"
            if not tests_dir.is_dir():
                collector.add(
                    rule="module-tests-dir",
                    message=(
                        f"`{_module_label(category, module_dir)}` is missing "
                        f"`tests/` directory — every module must have a test "
                        f"directory (§9.1, §9.3)."
                    ),
                    filepath=module_dir,
                    lineno=0,
                )
        collector.assert_clean("Modules missing tests/ directory")


# ═══════════════════════════════════════════════════════════════════════════
# Rule 5 — models/__init__.py imports model classes  (§4.3)
# ═══════════════════════════════════════════════════════════════════════════


class TestModelPackageInit:
    """When a module uses a ``models/`` package (not a single
    ``models.py``), its ``__init__.py`` must exist and should import model
    classes so Django's app registry can discover them.
    """

    @pytest.fixture
    def all_modules(self) -> list[tuple[str, Path]]:
        return _all_registered_modules()

    def test_models_init_exists(self, all_modules: list[tuple[str, Path]]) -> None:
        collector = ViolationCollector()
        for category, module_dir in all_modules:
            models_dir = module_dir / "models"
            if not models_dir.is_dir():
                continue  # uses models.py — not applicable

            init_file = models_dir / "__init__.py"
            if not init_file.exists():
                collector.add(
                    rule="models-init-py",
                    message=(
                        f"`{_module_label(category, module_dir)}/models/` "
                        f"is missing `__init__.py` — Django won't discover "
                        f"models without it (§4.3)."
                    ),
                    filepath=models_dir,
                    lineno=0,
                )
        collector.assert_clean("Model packages missing __init__.py")

    def test_models_init_imports_models_when_model_files_exist(self, all_modules: list[tuple[str, Path]]) -> None:
        """If the models/ package has any concrete ``.py`` files besides
        ``__init__.py``, the ``__init__.py`` should have ``import`` or
        ``from`` statements to re-export them.

        We only check this when model files are *not* empty (i.e., they
        contain class definitions) to avoid false positives during the
        bootstrap phase when files are placeholders.
        """
        collector = ViolationCollector()
        for category, module_dir in all_modules:
            models_dir = module_dir / "models"
            init_file = models_dir / "__init__.py"
            if not models_dir.is_dir() or not init_file.exists():
                continue

            # Count non-init .py files that contain class definitions
            model_files = [f for f in models_dir.glob("*.py") if f.name != "__init__.py" and _file_has_class(f)]
            if not model_files:
                continue  # bootstrap / empty — nothing to import yet

            # Check that __init__.py has some imports
            init_source = init_file.read_text(encoding="utf-8")
            try:
                tree = ast.parse(init_source, filename=str(init_file))
            except SyntaxError:
                continue

            has_imports = any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(tree))
            if not has_imports:
                file_names = ", ".join(f.name for f in model_files)
                collector.add(
                    rule="models-init-imports",
                    message=(
                        f"`{_module_label(category, module_dir)}/models/"
                        f"__init__.py` has no import statements but model "
                        f"files exist ({file_names}) — __init__.py must "
                        f"import model classes for Django discovery (§4.3)."
                    ),
                    filepath=init_file,
                    lineno=0,
                )
        collector.assert_clean("Model package __init__.py must import model classes")


def _file_has_class(filepath: Path) -> bool:
    """Return True if *filepath* contains at least one class definition."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except OSError, SyntaxError, UnicodeDecodeError:
        return False
    return any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))


# ═══════════════════════════════════════════════════════════════════════════
# Rule 6 — Application directories have commands/ and/or queries/
#           (§6, Appendix A)
# ═══════════════════════════════════════════════════════════════════════════


class TestApplicationDirectoryStructure:
    """When a module has an ``application/`` directory with actual code,
    it should contain ``commands/`` and/or ``queries/`` subdirectories.

    During bootstrap (empty ``application/``), the test is lenient.
    """

    @pytest.fixture
    def all_modules(self) -> list[tuple[str, Path]]:
        return _all_registered_modules()

    def test_application_has_commands_or_queries(self, all_modules: list[tuple[str, Path]]) -> None:
        collector = ViolationCollector()
        for category, module_dir in all_modules:
            app_dir = module_dir / "application"
            if not app_dir.is_dir():
                continue

            # Skip if application/ is essentially empty (bootstrap)
            py_files = [f for f in app_dir.rglob("*.py") if f.name != "__init__.py"]
            if not py_files:
                continue

            has_commands = (app_dir / "commands").is_dir()
            has_queries = (app_dir / "queries").is_dir()

            if not has_commands and not has_queries:
                collector.add(
                    rule="application-structure",
                    message=(
                        f"`{_module_label(category, module_dir)}/application/` "
                        f"has code but no `commands/` or `queries/` "
                        f"subdirectory — application layer should organize "
                        f"operations into these directories (§6, Appendix A)."
                    ),
                    filepath=app_dir,
                    lineno=0,
                )
        collector.assert_clean("Application directories should contain commands/ and/or queries/")


# ═══════════════════════════════════════════════════════════════════════════
# Additional structural checks
# ═══════════════════════════════════════════════════════════════════════════


class TestPlatformModulesStructure:
    """Platform modules follow the same basic structural requirements
    as business modules (minus public.py, which is optional for platform
    since business modules import platform directly).
    """

    def test_platform_modules_exist(self, platform_root: Path) -> None:
        """Verify the expected platform modules are present."""
        expected = {"identity", "tenancy", "authorization", "audit", "common"}
        if not platform_root.exists():
            pytest.skip("platform/ directory does not exist yet")

        actual = {d.name for d in discover_modules(platform_root)}
        missing = expected - actual
        if missing:
            pytest.fail(f"Expected platform modules not found: {sorted(missing)} (§2.4). Found: {sorted(actual)}")


class TestBusinessModulesExist:
    """Verify the expected initial business modules are present."""

    def test_initial_business_modules(self, modules_root: Path) -> None:
        expected = {"organizations", "programs", "fundraising", "beneficiaries"}
        if not modules_root.exists():
            pytest.skip("modules/ directory does not exist yet")

        actual = {d.name for d in discover_modules(modules_root)}
        missing = expected - actual
        if missing:
            pytest.fail(f"Expected business modules not found: {sorted(missing)} (§2.5). Found: {sorted(actual)}")
