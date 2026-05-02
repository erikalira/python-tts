from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_LAYER_IMPORTS = {
    "core": (
        "src.application",
        "src.infrastructure",
        "src.presentation",
        "src.desktop",
        "src.bot_runtime",
    ),
    "application": (
        "src.infrastructure",
        "src.presentation",
        "src.desktop",
        "src.bot_runtime",
    ),
    "presentation": (
        "src.infrastructure",
        "src.desktop",
        "src.bot_runtime",
    ),
    "infrastructure": (
        "src.presentation",
        "src.desktop",
        "src.bot_runtime",
    ),
}


def _iter_python_files(layer: str):
    layer_dir = REPO_ROOT / "src" / layer
    for path in sorted(layer_dir.rglob("*.py")):
        if path.name == "__pycache__":
            continue
        yield path


def _find_forbidden_imports(layer: str, forbidden_prefixes: tuple[str, ...]) -> list[str]:
    violations: list[str] = []
    for path in _iter_python_files(layer):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if _matches_forbidden_prefix(alias.name, forbidden_prefixes):
                        violations.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno} imports {alias.name}")
            elif (
                isinstance(node, ast.ImportFrom)
                and node.module
                and _matches_forbidden_prefix(node.module, forbidden_prefixes)
            ):
                violations.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno} imports from {node.module}")
    return violations


def _matches_forbidden_prefix(module_name: str, forbidden_prefixes: tuple[str, ...]) -> bool:
    return any(module_name == prefix or module_name.startswith(prefix + ".") for prefix in forbidden_prefixes)


def test_application_layer_does_not_import_infrastructure():
    violations = _find_forbidden_imports("application", ("src.infrastructure",))
    assert violations == [], "Application layer must not import infrastructure directly:\n" + "\n".join(violations)


def test_presentation_layer_does_not_import_infrastructure():
    violations = _find_forbidden_imports("presentation", ("src.infrastructure",))
    assert violations == [], "Presentation layer must not import infrastructure directly:\n" + "\n".join(violations)


def test_clean_architecture_layers_keep_inward_dependency_flow():
    violations: list[str] = []
    for layer, forbidden_prefixes in FORBIDDEN_LAYER_IMPORTS.items():
        violations.extend(_find_forbidden_imports(layer, forbidden_prefixes))

    assert violations == [], "Clean architecture dependency flow violations:\n" + "\n".join(violations)
