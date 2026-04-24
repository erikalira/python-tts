from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _iter_python_files(layer: str):
    layer_dir = REPO_ROOT / "src" / layer
    for path in sorted(layer_dir.rglob("*.py")):
        if path.name == "__pycache__":
            continue
        yield path


def _find_forbidden_imports(layer: str) -> list[str]:
    violations: list[str] = []
    for path in _iter_python_files(layer):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "src.infrastructure" or alias.name.startswith("src.infrastructure."):
                        violations.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno} imports {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and (
                    node.module == "src.infrastructure" or node.module.startswith("src.infrastructure.")
                ):
                    violations.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno} imports from {node.module}")
    return violations


def test_application_layer_does_not_import_infrastructure():
    violations = _find_forbidden_imports("application")
    assert violations == [], "Application layer must not import infrastructure directly:\n" + "\n".join(violations)


def test_presentation_layer_does_not_import_infrastructure():
    violations = _find_forbidden_imports("presentation")
    assert violations == [], "Presentation layer must not import infrastructure directly:\n" + "\n".join(violations)
