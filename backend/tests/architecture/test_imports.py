"""
Architecture enforcement — module import boundary tests.

These tests use AST analysis to verify that import dependencies follow the
architectural contracts defined in the Stage 0 Architecture Contracts
(§2.2, §2.3, §3.5, §9.3, §9.4).

No Django runtime or database is required.

Rules enforced
--------------
1. Platform modules (``abren_one.platform.*``) do NOT import from business
   modules (``abren_one.modules.*``).
2. Business modules do NOT import DRF (``rest_framework``) in ``domain/``
   or ``application/`` layers.
3. Cross-module imports go through ``public.py`` only — importing
   ``modules.X.domain``, ``modules.X.application``,
   ``modules.X.infrastructure``, or ``modules.X.models`` from outside
   module X is prohibited (must use ``modules.X.public``).
4. Interface layers do NOT bypass the application layer — no direct
   ``domain/`` or ``models/`` imports from ``interfaces/``.
5. No circular module-level dependencies between business modules.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.architecture.conftest import (
    MODULES_ROOT,
    ViolationCollector,
    discover_modules,
    extract_all_imports,
    is_submodule_of,
)

# ── Helpers ────────────────────────────────────────────────────────────────


def _module_name_from_filepath(filepath: Path) -> str | None:
    """Return the business-module name that *filepath* belongs to, or None."""
    try:
        rel = filepath.relative_to(MODULES_ROOT)
    except ValueError:
        return None
    parts = rel.parts
    return parts[0] if parts else None


def _layer_from_filepath(filepath: Path) -> str | None:
    """Return the intra-module layer name (domain, application, …) or None."""
    try:
        rel = filepath.relative_to(MODULES_ROOT)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) >= 2:
        return parts[1]  # e.g. "domain", "application", "interfaces", "models"
    return None


# ── Internal modules pattern for cross-module rule ─────────────────────────

# These are the "internal" subpackages of a business module.  Importing them
# from *outside* the owning module is prohibited (must go via public.py).
_INTERNAL_LAYERS = {"domain", "application", "infrastructure", "models"}


def _is_internal_cross_module_import(
    import_module: str,
    source_module_name: str | None,
) -> tuple[bool, str | None]:
    """Check if *import_module* reaches into another module's internals.

    Returns ``(True, target_module_name)`` when the import is a prohibited
    internal cross-module import, else ``(False, None)``.
    """
    prefix = "abren_one.modules."
    if not import_module.startswith(prefix):
        return False, None

    # e.g. "abren_one.modules.organizations.domain.policies"
    remainder = import_module[len(prefix) :]  # "organizations.domain.policies"
    parts = remainder.split(".")
    if len(parts) < 2:
        # Importing the module root or its public.py — allowed
        return False, None

    target_module = parts[0]  # "organizations"
    target_subpackage = parts[1]  # "domain"

    # Same-module internal imports are perfectly fine
    if target_module == source_module_name:
        return False, None

    # If the target subpackage is one of the internal layers, it's prohibited
    if target_subpackage in _INTERNAL_LAYERS:
        return True, target_module

    return False, None


# ═══════════════════════════════════════════════════════════════════════════
# Rule 1 — Platform modules must NOT import business modules  (§2.2, §2.3)
# ═══════════════════════════════════════════════════════════════════════════


class TestPlatformDoesNotImportModules:
    """Platform code must never depend on business-module code.

    Dependency direction: modules → platform, never the reverse.
    """

    def test_no_platform_imports_from_modules(self, platform_root: Path) -> None:
        collector = ViolationCollector()
        for imp in extract_all_imports(platform_root):
            if is_submodule_of(imp.module, "abren_one.modules"):
                collector.add(
                    rule="platform-no-modules",
                    message=(
                        f"Platform file imports business module: "
                        f"`{imp.module}` — platform must not depend on "
                        f"business modules (§2.2)."
                    ),
                    filepath=imp.filepath,
                    lineno=imp.lineno,
                )
        collector.assert_clean("Platform modules must not import from abren_one.modules.*")


# ═══════════════════════════════════════════════════════════════════════════
# Rule 2 — Business domain/application layers must NOT import DRF  (§2.2)
# ═══════════════════════════════════════════════════════════════════════════


class TestBusinessLayersDoNotImportDRF:
    """Domain and application layers must remain free of HTTP/DRF coupling.

    DRF imports (``rest_framework``) are only permitted in the
    ``interfaces/`` layer.
    """

    _DRF_PREFIXES = ("rest_framework",)
    _RESTRICTED_LAYERS = {"domain", "application"}

    def test_no_drf_in_domain_or_application(self, modules_root: Path) -> None:
        collector = ViolationCollector()

        for module_dir in discover_modules(modules_root):
            module_name = module_dir.name
            for layer in self._RESTRICTED_LAYERS:
                layer_dir = module_dir / layer
                if not layer_dir.exists():
                    continue
                for imp in extract_all_imports(layer_dir):
                    if any(is_submodule_of(imp.module, pfx) for pfx in self._DRF_PREFIXES):
                        collector.add(
                            rule="no-drf-in-domain-application",
                            message=(
                                f"Module `{module_name}/{layer}` imports DRF: "
                                f"`{imp.module}` — domain and application "
                                f"layers must not depend on rest_framework (§2.2)."
                            ),
                            filepath=imp.filepath,
                            lineno=imp.lineno,
                        )

        collector.assert_clean("Business module domain/application layers must not import DRF")


# ═══════════════════════════════════════════════════════════════════════════
# Rule 3 — Cross-module imports go through public.py only  (§2.3, §3.5)
# ═══════════════════════════════════════════════════════════════════════════


class TestCrossModuleImportsThroughPublic:
    """When module Y imports from module X, it must use
    ``abren_one.modules.X.public`` — never reach into X's internal layers.

    Internal layers: ``domain/``, ``application/``, ``infrastructure/``,
    ``models/``.

    Imports within the same module (X→X) are unrestricted.
    Imports to ``abren_one.modules.X`` (root) or
    ``abren_one.modules.X.public`` are allowed.
    """

    def test_no_internal_cross_module_imports(self, modules_root: Path) -> None:
        collector = ViolationCollector()

        for module_dir in discover_modules(modules_root):
            source_module = module_dir.name
            for imp in extract_all_imports(module_dir):
                is_violation, target_module = _is_internal_cross_module_import(imp.module, source_module)
                if is_violation:
                    collector.add(
                        rule="cross-module-public-only",
                        message=(
                            f"Module `{source_module}` imports internal "
                            f"subpackage of module `{target_module}`: "
                            f"`{imp.module}` — cross-module imports must go "
                            f"through `abren_one.modules.{target_module}.public` "
                            f"(§2.3, §3.5)."
                        ),
                        filepath=imp.filepath,
                        lineno=imp.lineno,
                    )

        collector.assert_clean("Cross-module imports must go through public.py, not internal subpackages")

    def test_platform_cross_module_imports_via_public(self, platform_root: Path) -> None:
        """Platform should not reach into module internals either (it
        shouldn't import modules at all — Rule 1 — but this catches the
        *specific* internal-import variant for completeness).
        """
        collector = ViolationCollector()

        for imp in extract_all_imports(platform_root):
            is_violation, target_module = _is_internal_cross_module_import(imp.module, source_module_name=None)
            if is_violation:
                collector.add(
                    rule="platform-cross-module-public-only",
                    message=(
                        f"Platform imports internal subpackage of module "
                        f"`{target_module}`: `{imp.module}` — must use "
                        f"`abren_one.modules.{target_module}.public` (§2.3)."
                    ),
                    filepath=imp.filepath,
                    lineno=imp.lineno,
                )

        collector.assert_clean("Platform must not import module internals")

    def test_integrations_cross_module_imports_via_public(
        self,
        integrations_root: Path,
    ) -> None:
        """Integration modules must also go through ``public.py``."""
        if not integrations_root.exists():
            pytest.skip("integrations/ directory does not exist yet")

        collector = ViolationCollector()

        for imp in extract_all_imports(integrations_root):
            is_violation, target_module = _is_internal_cross_module_import(imp.module, source_module_name=None)
            if is_violation:
                collector.add(
                    rule="integration-cross-module-public-only",
                    message=(
                        f"Integration code imports internal subpackage of "
                        f"module `{target_module}`: `{imp.module}` — must "
                        f"use `abren_one.modules.{target_module}.public` "
                        f"(§2.3)."
                    ),
                    filepath=imp.filepath,
                    lineno=imp.lineno,
                )

        collector.assert_clean("Integration modules must not import module internals")

    def test_integration_tests_import_via_public_only(
        self,
        backend_root: Path,
    ) -> None:
        """Integration tests under tests/integration/ must interact with
        business modules exclusively via *.public, never reaching into
        internal application, domain, models, or infrastructure layers.
        """
        integration_tests_dir = backend_root / "tests" / "integration"
        if not integration_tests_dir.exists():
            return

        collector = ViolationCollector()
        for imp in extract_all_imports(integration_tests_dir):
            is_violation, target_module = _is_internal_cross_module_import(
                imp.module,
                source_module_name=None,
            )
            if is_violation:
                collector.add(
                    rule="integration-test-public-only",
                    message=(
                        f"Integration test `{imp.filepath.name}` imports internal subpackage of "
                        f"module `{target_module}`: `{imp.module}` — must use "
                        f"`abren_one.modules.{target_module}.public`."
                    ),
                    filepath=imp.filepath,
                    lineno=imp.lineno,
                )

        collector.assert_clean("Integration tests must import through public.py only")


# ═══════════════════════════════════════════════════════════════════════════
# Rule 4 — Interface layers do NOT bypass the application layer  (§2.2)
# ═══════════════════════════════════════════════════════════════════════════


class TestInterfaceLayerDoesNotBypassApplication:
    """Views and serializers in ``interfaces/`` must call application
    commands and queries — they must not directly import from ``domain/``
    or ``models/`` (within the same module) to avoid bypassing the
    application layer.

    Allowed from ``interfaces/``:
    - ``abren_one.modules.X.application.*``
    - ``abren_one.modules.X.public``
    - ``abren_one.platform.*``
    - ``rest_framework.*``
    - ``django.*``
    - standard library

    Disallowed:
    - ``abren_one.modules.X.domain.*``
    - ``abren_one.modules.X.models.*``
    - ``abren_one.modules.X.infrastructure.*``
    """

    _BYPASSED_LAYERS = {"domain", "models", "infrastructure"}

    def test_no_direct_domain_or_model_imports_in_interfaces(self, modules_root: Path) -> None:
        collector = ViolationCollector()

        for module_dir in discover_modules(modules_root):
            module_name = module_dir.name
            interfaces_dir = module_dir / "interfaces"
            if not interfaces_dir.exists():
                continue

            prefix = f"abren_one.modules.{module_name}."

            for imp in extract_all_imports(interfaces_dir):
                if not imp.module.startswith(prefix):
                    continue  # importing outside the module — other rules apply
                remainder = imp.module[len(prefix) :]
                top_subpackage = remainder.split(".")[0]

                if top_subpackage in self._BYPASSED_LAYERS:
                    collector.add(
                        rule="interface-no-bypass",
                        message=(
                            f"Interface layer of `{module_name}` directly "
                            f"imports `{imp.module}` — interface code must "
                            f"go through the application layer, not import "
                            f"`{top_subpackage}/` directly (§2.2)."
                        ),
                        filepath=imp.filepath,
                        lineno=imp.lineno,
                    )

        collector.assert_clean("Interface layers must not bypass the application layer")


# ═══════════════════════════════════════════════════════════════════════════
# Rule 5 — No circular module-level dependencies  (§9.3)
# ═══════════════════════════════════════════════════════════════════════════


class TestNoCircularModuleDependencies:
    """Detect circular dependencies between business modules.

    Builds a directed graph of ``module A imports module B`` (considering
    only cross-module abren_one.modules.* imports), then checks for cycles.
    """

    def _build_dependency_graph(self, modules_root: Path) -> dict[str, set[str]]:
        """Return {source_module: {target_module, …}} graph."""
        graph: dict[str, set[str]] = {}
        prefix = "abren_one.modules."

        for module_dir in discover_modules(modules_root):
            src_name = module_dir.name
            if src_name not in graph:
                graph[src_name] = set()

            for imp in extract_all_imports(module_dir):
                if not imp.module.startswith(prefix):
                    continue
                remainder = imp.module[len(prefix) :]
                target_name = remainder.split(".")[0]
                if target_name != src_name:
                    graph[src_name].add(target_name)

        return graph

    @staticmethod
    def _find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
        """Simple DFS cycle detection returning all distinct cycles."""
        WHITE, GRAY, BLACK = 0, 1, 2  # noqa: N806
        color: dict[str, int] = {n: WHITE for n in graph}
        path: list[str] = []
        cycles: list[list[str]] = []

        def dfs(node: str) -> None:
            color[node] = GRAY
            path.append(node)
            for neighbour in graph.get(node, set()):
                if neighbour not in color:
                    continue
                if color[neighbour] == GRAY:
                    # Found a cycle — extract it
                    cycle_start = path.index(neighbour)
                    cycle = path[cycle_start:] + [neighbour]
                    cycles.append(cycle)
                elif color[neighbour] == WHITE:
                    dfs(neighbour)
            path.pop()
            color[node] = BLACK

        for node in graph:
            if color[node] == WHITE:
                dfs(node)

        return cycles

    def test_no_circular_dependencies(self, modules_root: Path) -> None:
        graph = self._build_dependency_graph(modules_root)
        cycles = self._find_cycles(graph)

        if cycles:
            formatted = "\n".join(f"  • {' → '.join(c)}" for c in cycles)
            pytest.fail(
                f"Circular module dependencies detected (§9.3):\n{formatted}\n"
                f"Break the cycle by using events, public interfaces, "
                f"or restructuring the dependency."
            )

    def test_dependencies_comply_with_allowed_dag(self, modules_root: Path) -> None:
        """Enforce that module cross-dependencies strictly comply with the
        declared architectural dependency directed acyclic graph (DAG).
        Any new cross-module dependency requires deliberate architectural approval.
        """
        allowed_dag: dict[str, set[str]] = {
            "organizations": set(),
            "programs": {"organizations"},
            "beneficiaries": {"organizations", "programs", "inventory"},
            "fundraising": {"organizations", "programs", "finance"},
            "procurement": {"organizations", "programs"},
            "finance": {"organizations", "programs"},
            "inventory": {"organizations", "procurement", "finance"},
        }

        graph = self._build_dependency_graph(modules_root)
        collector = ViolationCollector()

        for source_module, actual_deps in sorted(graph.items()):
            allowed_deps = allowed_dag.get(source_module, set())
            unauthorized_deps = actual_deps - allowed_deps
            if unauthorized_deps:
                collector.add(
                    rule="allowed-dependency-dag",
                    message=(
                        f"Module `{source_module}` has unauthorized cross-module dependencies: "
                        f"{sorted(unauthorized_deps)}. Allowed dependencies for `{source_module}`: "
                        f"{sorted(allowed_deps)}."
                    ),
                    filepath=modules_root / source_module,
                    lineno=0,
                )

        collector.assert_clean("Cross-module dependencies must strictly adhere to the declared DAG")


# ═══════════════════════════════════════════════════════════════════════════
# Rule 6 — Application/domain layers must not import HTTP concepts  (§2.2)
# ═══════════════════════════════════════════════════════════════════════════


class TestApplicationDoesNotImportHTTP:
    """Application and domain layers must be free of HTTP-level concepts.

    This catches ``django.http``, ``django.urls``, and ``rest_framework``
    imports within ``domain/`` and ``application/`` layers.
    """

    _HTTP_MODULES = (
        "django.http",
        "django.urls",
        "rest_framework",
    )
    _RESTRICTED_LAYERS = {"domain", "application"}

    def test_no_http_in_domain_or_application(self, modules_root: Path) -> None:
        collector = ViolationCollector()

        for module_dir in discover_modules(modules_root):
            module_name = module_dir.name
            for layer in self._RESTRICTED_LAYERS:
                layer_dir = module_dir / layer
                if not layer_dir.exists():
                    continue
                for imp in extract_all_imports(layer_dir):
                    if any(is_submodule_of(imp.module, http_mod) for http_mod in self._HTTP_MODULES):
                        collector.add(
                            rule="no-http-in-domain-application",
                            message=(
                                f"Module `{module_name}/{layer}` imports "
                                f"HTTP-level module: `{imp.module}` — "
                                f"domain and application layers must not "
                                f"depend on HTTP concepts (§2.2)."
                            ),
                            filepath=imp.filepath,
                            lineno=imp.lineno,
                        )

        collector.assert_clean("Domain/application layers must not import HTTP modules")


# ═══════════════════════════════════════════════════════════════════════════
# Rule 7 — Models/infrastructure must not import DRF  (§2.2)
# ═══════════════════════════════════════════════════════════════════════════


class TestModelsDoNotImportDRF:
    """Model and infrastructure layers must not depend on DRF."""

    _RESTRICTED_LAYERS = {"models", "infrastructure"}

    def test_no_drf_in_models_or_infrastructure(self, modules_root: Path) -> None:
        collector = ViolationCollector()

        for module_dir in discover_modules(modules_root):
            module_name = module_dir.name
            for layer in self._RESTRICTED_LAYERS:
                layer_dir = module_dir / layer
                if not layer_dir.exists():
                    continue
                for imp in extract_all_imports(layer_dir):
                    if is_submodule_of(imp.module, "rest_framework"):
                        collector.add(
                            rule="no-drf-in-models",
                            message=(
                                f"Module `{module_name}/{layer}` imports DRF: "
                                f"`{imp.module}` — models and infrastructure "
                                f"must not depend on rest_framework (§2.2)."
                            ),
                            filepath=imp.filepath,
                            lineno=imp.lineno,
                        )

        collector.assert_clean("Models/infrastructure must not import rest_framework")


# ═══════════════════════════════════════════════════════════════════════════
# Rule 8 — Relative import resolution integrity
# ═══════════════════════════════════════════════════════════════════════════


class TestRelativeImportResolution:
    """Verify that relative imports are resolved and cannot circumvent boundaries."""

    def test_relative_import_resolution_detects_prohibited_cross_module(self, tmp_path: Path) -> None:
        from tests.architecture.conftest import extract_imports

        fake_file = (
            tmp_path / "backend" / "src" / "abren_one" / "modules" / "programs" / "application" / "commands" / "fake.py"
        )
        fake_file.parent.mkdir(parents=True)
        fake_file.write_text("from ....organizations.domain import policies\n")

        imports = extract_imports(fake_file)
        assert len(imports) == 1
        assert imports[0].module == "abren_one.modules.organizations.domain"
        is_violation, target = _is_internal_cross_module_import(imports[0].module, "programs")
        assert is_violation is True
        assert target == "organizations"


# ═══════════════════════════════════════════════════════════════════════════
# Rule 9 — Deliberate violation rejection (§3.5)
# ═══════════════════════════════════════════════════════════════════════════


class TestEnforcementDetectsDeliberateViolations:
    """Verify that architecture enforcement detects and rejects prohibited patterns (§3.5)."""

    def test_detects_platform_importing_business_module(self, tmp_path: Path) -> None:
        from tests.architecture.conftest import extract_imports

        fake_file = tmp_path / "backend" / "src" / "abren_one" / "platform" / "tenancy" / "bad.py"
        fake_file.parent.mkdir(parents=True)
        fake_file.write_text("from abren_one.modules.organizations.models import Organization\n")

        imports = extract_imports(fake_file)
        assert len(imports) == 1
        assert is_submodule_of(imports[0].module, "abren_one.modules")

    def test_detects_domain_importing_drf(self, tmp_path: Path) -> None:
        from tests.architecture.conftest import extract_imports

        fake_file = tmp_path / "backend" / "src" / "abren_one" / "modules" / "programs" / "domain" / "bad.py"
        fake_file.parent.mkdir(parents=True)
        fake_file.write_text("import rest_framework\n")

        imports = extract_imports(fake_file)
        assert len(imports) == 1
        assert is_submodule_of(imports[0].module, "rest_framework")

    def test_detects_cross_module_internal_import(self, tmp_path: Path) -> None:
        from tests.architecture.conftest import extract_imports

        fake_file = tmp_path / "backend" / "src" / "abren_one" / "modules" / "programs" / "application" / "bad.py"
        fake_file.parent.mkdir(parents=True)
        fake_file.write_text("from abren_one.modules.organizations.models.organization import Organization\n")

        imports = extract_imports(fake_file)
        is_violation, target = _is_internal_cross_module_import(imports[0].module, "programs")
        assert is_violation is True
        assert target == "organizations"

    def test_detects_interface_bypassing_application(self, tmp_path: Path) -> None:
        from tests.architecture.conftest import extract_imports

        fake_file = (
            tmp_path / "backend" / "src" / "abren_one" / "modules" / "programs" / "interfaces" / "api" / "bad.py"
        )
        fake_file.parent.mkdir(parents=True)
        fake_file.write_text("from abren_one.modules.programs.models.program import Program\n")

        imports = extract_imports(fake_file)
        assert len(imports) == 1
        assert "models" in TestInterfaceLayerDoesNotBypassApplication._BYPASSED_LAYERS
