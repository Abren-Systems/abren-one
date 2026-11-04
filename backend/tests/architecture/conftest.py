"""
Architecture test fixtures and AST analysis helpers.

These fixtures provide common paths and helper functions for architecture
enforcement tests that analyse source code structure without running Django.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

import pytest

# ── Absolute anchor paths ──────────────────────────────────────────────────

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent  # backend/
SRC_ROOT = BACKEND_ROOT / "src"
PACKAGE_ROOT = SRC_ROOT / "abren_one"
PLATFORM_ROOT = PACKAGE_ROOT / "platform"
MODULES_ROOT = PACKAGE_ROOT / "modules"
INTEGRATIONS_ROOT = PACKAGE_ROOT / "integrations"


# ── Path fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def backend_root() -> Path:
    return BACKEND_ROOT


@pytest.fixture
def src_root() -> Path:
    return SRC_ROOT


@pytest.fixture
def package_root() -> Path:
    return PACKAGE_ROOT


@pytest.fixture
def platform_root() -> Path:
    return PLATFORM_ROOT


@pytest.fixture
def modules_root() -> Path:
    return MODULES_ROOT


@pytest.fixture
def integrations_root() -> Path:
    return INTEGRATIONS_ROOT


# ── Discovery helpers ──────────────────────────────────────────────────────

def discover_python_files(root: Path) -> list[Path]:
    """Return all .py files under *root*, sorted for deterministic output."""
    if not root.exists():
        return []
    return sorted(root.rglob("*.py"))


def discover_modules(root: Path) -> list[Path]:
    """Return immediate subdirectories of *root* that look like Python packages.

    A directory qualifies if it contains ``__init__.py`` **or** any ``.py``
    file (to catch bootstrap modules that haven't been fully scaffolded yet).
    """
    if not root.exists():
        return []
    return sorted(
        d
        for d in root.iterdir()
        if d.is_dir()
        and not d.name.startswith("_")
        and (
            (d / "__init__.py").exists()
            or any(d.rglob("*.py"))
        )
    )


# ── AST import extraction ─────────────────────────────────────────────────

@dataclass(frozen=True)
class ImportInfo:
    """A single import found via AST analysis."""

    module: str  # Fully-qualified module path
    names: tuple[str, ...]  # Names imported (empty for plain ``import X``)
    filepath: Path  # Source file where the import was found
    lineno: int  # Line number of the import statement

    def __str__(self) -> str:
        names_part = f" ({', '.join(self.names)})" if self.names else ""
        return f"{self.filepath}:{self.lineno} → {self.module}{names_part}"


def extract_imports(filepath: Path) -> list[ImportInfo]:
    """Parse a Python file and return every import as an ``ImportInfo``.

    Uses the ``ast`` module so no code is actually executed.  Returns an
    empty list for files that cannot be parsed.
    """
    try:
        source = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return []

    imports: list[ImportInfo] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(
                    ImportInfo(
                        module=alias.name,
                        names=(),
                        filepath=filepath,
                        lineno=node.lineno,
                    )
                )
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue  # relative import with no module (e.g., ``from . import x``)
            names = tuple(alias.name for alias in node.names)
            imports.append(
                ImportInfo(
                    module=node.module,
                    names=names,
                    filepath=filepath,
                    lineno=node.lineno,
                )
            )
    return imports


def extract_all_imports(root: Path) -> list[ImportInfo]:
    """Extract imports from every ``.py`` file under *root*."""
    result: list[ImportInfo] = []
    for py_file in discover_python_files(root):
        result.extend(extract_imports(py_file))
    return result


# ── Dotted-path helpers ────────────────────────────────────────────────────

def filepath_to_module(filepath: Path) -> str:
    """Convert a filesystem path to a dotted module path relative to ``src/``.

    Example::

        backend/src/abren_one/modules/organizations/domain/policies.py
        → abren_one.modules.organizations.domain.policies
    """
    relative = filepath.relative_to(SRC_ROOT)
    parts = list(relative.parts)
    # Remove the ``.py`` suffix (or ``__init__`` for packages)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    elif parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]
    return ".".join(parts)


def module_name_from_path(module_dir: Path) -> str:
    """Return the short name of a module directory (last component)."""
    return module_dir.name


def is_submodule_of(import_path: str, parent: str) -> bool:
    """Return True if *import_path* is equal to or a child of *parent*."""
    return import_path == parent or import_path.startswith(parent + ".")


# ── Violation collection helpers ───────────────────────────────────────────

@dataclass
class Violation:
    """A single architecture-rule violation."""

    rule: str
    message: str
    filepath: Path
    lineno: int

    def __str__(self) -> str:
        return f"[{self.rule}] {self.filepath}:{self.lineno} — {self.message}"


@dataclass
class ViolationCollector:
    """Accumulates violations across multiple checks, then asserts at the end."""

    violations: list[Violation] = field(default_factory=list)

    def add(self, rule: str, message: str, filepath: Path, lineno: int) -> None:
        self.violations.append(
            Violation(rule=rule, message=message, filepath=filepath, lineno=lineno)
        )

    def assert_clean(self, header: str = "Architecture violations found") -> None:
        if not self.violations:
            return
        details = "\n".join(f"  • {v}" for v in self.violations)
        pytest.fail(f"{header} ({len(self.violations)}):\n{details}")
