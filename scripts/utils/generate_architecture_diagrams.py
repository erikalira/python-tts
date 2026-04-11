"""Generate architecture Mermaid diagrams from pyreverse output.

This script keeps a fully automatic, GitHub-friendly diagram set under
``docs/diagrams/generated``. The committed output is Markdown with an
embedded Mermaid code fence so it renders directly on GitHub.
"""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from pylint import run_pyreverse
except ImportError:  # pragma: no cover - handled at runtime for CLI usage
    run_pyreverse = None


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "docs" / "diagrams" / "generated"


@dataclass(frozen=True)
class DiagramTarget:
    """Describe one diagram generation target."""

    slug: str
    title: str
    description: str
    modules: tuple[str, ...]


TARGETS = (
    DiagramTarget(
        slug="shared",
        title="Generated Shared Diagram",
        description="Automatic class diagram for shared core and application modules.",
        modules=("src.core", "src.application"),
    ),
    DiagramTarget(
        slug="bot-runtime",
        title="Generated Bot Runtime Diagram",
        description=(
            "Automatic class diagram for bot runtime, presentation, and infrastructure modules."
        ),
        modules=("src.bot_runtime", "src.presentation", "src.infrastructure"),
    ),
    DiagramTarget(
        slug="desktop-runtime",
        title="Generated Desktop Runtime Diagram",
        description=(
            "Automatic class diagram for Desktop App runtime, GUI, services, and config modules."
        ),
        modules=(
            "src.desktop.app",
            "src.desktop.gui",
            "src.desktop.services",
            "src.desktop.config",
        ),
    ),
)


def _pyreverse_args(target: DiagramTarget) -> list[str]:
    """Build the pyreverse argument list for one diagram target."""

    return [
        "-o",
        "mmd",
        "-d",
        str(OUTPUT_DIR),
        "-p",
        target.slug.replace("-", "_"),
        *target.modules,
    ]


def _run_pyreverse(target: DiagramTarget) -> Path:
    """Generate one Mermaid diagram file through the pyreverse Python API."""

    if run_pyreverse is None:
        raise RuntimeError("pylint is not installed in the active environment")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    previous_cwd = Path.cwd()
    try:
        # pyreverse resolves imports relative to the current working directory.
        # Keeping execution rooted at the repository mirrors the CLI behavior.
        os.chdir(ROOT)
        try:
            run_pyreverse(_pyreverse_args(target))
        except SystemExit as exc:
            exit_code = exc.code if isinstance(exc.code, int) else 1
        else:
            exit_code = 0
    finally:
        os.chdir(previous_cwd)
    if exit_code != 0:
        raise RuntimeError(f"pyreverse failed with exit code {exit_code}")

    generated_name = f"classes_{target.slug.replace('-', '_')}.mmd"
    generated_path = OUTPUT_DIR / generated_name
    if not generated_path.exists():
        raise FileNotFoundError(
            f"pyreverse did not create expected file: {generated_path}"
        )

    final_path = OUTPUT_DIR / f"{target.slug}.mmd"
    if final_path.exists():
        final_path.unlink()
    shutil.move(str(generated_path), str(final_path))

    packages_name = f"packages_{target.slug.replace('-', '_')}.mmd"
    packages_path = OUTPUT_DIR / packages_name
    if packages_path.exists():
        packages_path.unlink()

    return final_path


def _wrap_mermaid(target: DiagramTarget, mermaid_path: Path) -> None:
    markdown_path = OUTPUT_DIR / f"{target.slug}.md"
    mermaid_content = mermaid_path.read_text(encoding="utf-8").strip()
    markdown = (
        f"# {target.title}\n\n"
        f"{target.description}\n\n"
        "```mermaid\n"
        f"{mermaid_content}\n"
        "```\n"
    )
    markdown_path.write_text(markdown, encoding="utf-8")
    mermaid_path.unlink()


def _write_index(targets: tuple[DiagramTarget, ...]) -> None:
    index_path = OUTPUT_DIR / "README.md"
    lines = [
        "# Generated Architecture Diagrams",
        "",
        "These diagrams are generated automatically with `pyreverse`.",
        "",
        "## Files",
        "",
    ]

    for target in targets:
        lines.append(f"- [{target.slug}.md]({target.slug}.md): {target.description}")

    lines.extend(
        [
            "",
            "## Regeneration",
            "",
            "Run:",
            "",
            "```powershell",
            "python scripts/utils/generate_architecture_diagrams.py",
            "```",
        ]
    )

    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Generate Markdown-wrapped Mermaid diagrams and an index page."""

    generated: list[DiagramTarget] = []
    try:
        for target in TARGETS:
            mermaid_path = _run_pyreverse(target)
            _wrap_mermaid(target, mermaid_path)
            generated.append(target)
    except RuntimeError as exc:
        print("Failed to run pyreverse.", file=sys.stderr)
        print(
            "Install pylint in the active environment or run this script "
            "from the project's configured environment.",
            file=sys.stderr,
        )
        print(str(exc), file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    _write_index(tuple(generated))
    print(f"Generated {len(generated)} diagram sets in {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
