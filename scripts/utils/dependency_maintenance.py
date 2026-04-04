#!/usr/bin/env python
"""Utilities for dependency maintenance in this repository.

This script helps with three recurring tasks:

1. Inspect requirement files and compare them with the current environment.
2. Rewrite requirement constraints using versions already installed locally.
3. Validate a dependency migration with tests and import smoke checks.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import subprocess  # nosec B404 - used with fixed argument lists and explicit command validation
import sys
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


DEFAULT_REQUIREMENT_FILES = ("requirements.txt", "requirements-test.txt")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_PYTHON = str(Path(sys.executable).resolve())
OUTDATED_COMMAND = (REPOSITORY_PYTHON, "-m", "pip", "list", "--outdated", "--format=json")
UNIT_TEST_COMMAND = (REPOSITORY_PYTHON, "-m", "pytest", "tests/unit")
INTEGRATION_TEST_COMMAND = (REPOSITORY_PYTHON, "-m", "pytest", "tests/integration")
IMPORT_SMOKE_COMMAND = (REPOSITORY_PYTHON, "-c", "import app; import src.bot")


@dataclass(frozen=True)
class RequirementEntry:
    """A parsed requirement line from a requirements file."""

    package: str
    normalized_name: str
    rendered_name: str
    operator: str
    version: str
    original_line: str
    line_number: int


def normalize_package_name(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def parse_requirement_line(line: str, line_number: int) -> RequirementEntry | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    base = stripped.split("#", 1)[0].strip()
    if not base or base.startswith("-"):
        return None

    match = re.match(
        r"^(?P<name>[A-Za-z0-9_.-]+(?:\[[A-Za-z0-9_,.-]+\])?)\s*"
        r"(?P<operator>==|>=|<=|~=|!=|>|<)?\s*"
        r"(?P<version>[^;,\s]+)?",
        base,
    )
    if not match:
        return None

    rendered_name = match.group("name") or ""
    operator = match.group("operator") or ""
    version = match.group("version") or ""
    package = rendered_name.split("[", 1)[0]

    return RequirementEntry(
        package=package,
        normalized_name=normalize_package_name(package),
        rendered_name=rendered_name,
        operator=operator,
        version=version,
        original_line=line,
        line_number=line_number,
    )


def load_requirements(path: Path) -> list[RequirementEntry]:
    entries: list[RequirementEntry] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        entry = parse_requirement_line(line, index)
        if entry is not None:
            entries.append(entry)
    return entries


def get_installed_version(package_name: str) -> str | None:
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def is_safe_python_executable(executable: str) -> bool:
    try:
        resolved = Path(executable).resolve(strict=False)
    except OSError:
        return False

    return str(resolved) == REPOSITORY_PYTHON


def validate_command(command: list[str]) -> None:
    if not command:
        raise ValueError("Command cannot be empty.")

    executable = command[0]
    if not is_safe_python_executable(executable):
        raise ValueError("Only the current repository Python interpreter may be executed.")

    allowed_patterns = (
        list(OUTDATED_COMMAND),
        list(UNIT_TEST_COMMAND),
        list(INTEGRATION_TEST_COMMAND),
        list(IMPORT_SMOKE_COMMAND),
    )

    if command not in allowed_patterns:
        raise ValueError(f"Unsafe command rejected: {command!r}")


def run_outdated_command() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(OUTDATED_COMMAND),
        capture_output=True,
        check=True,
        text=True,
        shell=False,
        cwd=PROJECT_ROOT,
    )  # nosec B603 - fixed safe command without shell expansion


def run_unit_tests_command() -> subprocess.CompletedProcess[None]:
    return subprocess.run(
        list(UNIT_TEST_COMMAND),
        shell=False,
        cwd=PROJECT_ROOT,
    )  # nosec B603 - fixed safe command without shell expansion


def run_integration_tests_command() -> subprocess.CompletedProcess[None]:
    return subprocess.run(
        list(INTEGRATION_TEST_COMMAND),
        shell=False,
        cwd=PROJECT_ROOT,
    )  # nosec B603 - fixed safe command without shell expansion


def run_import_smoke_command() -> subprocess.CompletedProcess[None]:
    return subprocess.run(
        list(IMPORT_SMOKE_COMMAND),
        shell=False,
        cwd=PROJECT_ROOT,
    )  # nosec B603 - fixed safe command without shell expansion


def get_outdated_versions() -> dict[str, str]:
    validate_command(list(OUTDATED_COMMAND))
    try:
        result = run_outdated_command()
    except subprocess.CalledProcessError:
        return {}

    try:
        payload = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return {}

    outdated: dict[str, str] = {}
    for item in payload:
        name = item.get("name")
        latest = item.get("latest_version")
        if name and latest:
            outdated[normalize_package_name(name)] = str(latest)
    return outdated


def build_requirement_report(
    requirement_files: Iterable[Path],
    include_outdated: bool,
) -> str:
    outdated_versions = get_outdated_versions() if include_outdated else {}
    lines = []

    for path in requirement_files:
        lines.append(f"[{path.as_posix()}]")
        if not path.exists():
            lines.append("  missing")
            lines.append("")
            continue

        entries = load_requirements(path)
        if not entries:
            lines.append("  no supported requirement entries found")
            lines.append("")
            continue

        for entry in entries:
            installed = get_installed_version(entry.package) or "not-installed"
            latest = outdated_versions.get(entry.normalized_name)
            status = "up-to-date"
            if latest and installed != latest:
                status = f"update-available -> {latest}"
            constraint = f"{entry.operator}{entry.version}" if entry.operator else "(unbounded)"
            lines.append(
                "  "
                f"{entry.rendered_name}: required {constraint}, "
                f"installed {installed}, status {status}"
            )
        lines.append("")

    return "\n".join(lines).rstrip()


def resolve_target_version(package: str, explicit_version: str | None) -> str:
    if explicit_version:
        return explicit_version

    installed = get_installed_version(package)
    if not installed:
        raise ValueError(
            f"Package '{package}' is not installed in the current interpreter. "
            "Pass --version or install it first."
        )
    return installed


def rewrite_requirement_lines(
    path: Path,
    package: str,
    version: str,
    operator: str,
) -> bool:
    if not path.exists():
        return False

    normalized_target = normalize_package_name(package)
    lines = path.read_text(encoding="utf-8").splitlines()
    changed = False
    rewritten_lines: list[str] = []

    for index, line in enumerate(lines, start=1):
        entry = parse_requirement_line(line, index)
        if entry is None or entry.normalized_name != normalized_target:
            rewritten_lines.append(line)
            continue

        rewritten_lines.append(f"{entry.rendered_name}{operator}{version}")
        changed = True

    if changed:
        path.write_text("\n".join(rewritten_lines) + "\n", encoding="utf-8")
    return changed


def run_command(command: list[str]) -> int:
    validate_command(command)
    print(f"$ {' '.join(command)}")
    command_tuple = tuple(command)
    if command_tuple == UNIT_TEST_COMMAND:
        completed = run_unit_tests_command()
    elif command_tuple == INTEGRATION_TEST_COMMAND:
        completed = run_integration_tests_command()
    elif command_tuple == IMPORT_SMOKE_COMMAND:
        completed = run_import_smoke_command()
    else:
        raise ValueError(f"Unsafe command rejected: {command!r}")
    return completed.returncode


def command_report(args: argparse.Namespace) -> int:
    files = [Path(item) for item in args.files]
    report = build_requirement_report(
        requirement_files=files,
        include_outdated=args.outdated,
    )
    print(report)
    return 0


def command_pin(args: argparse.Namespace) -> int:
    version = resolve_target_version(args.package, args.version)
    files = [Path(item) for item in args.files]
    changed_files: list[str] = []

    for path in files:
        if rewrite_requirement_lines(path, args.package, version, args.operator):
            changed_files.append(path.as_posix())

    if not changed_files:
        print(
            f"No requirement entry for '{args.package}' was found in: "
            f"{', '.join(path.as_posix() for path in files)}"
        )
        return 1

    print(
        f"Updated {args.package} to {args.operator}{version} in "
        f"{', '.join(changed_files)}"
    )
    return 0


def command_validate(args: argparse.Namespace) -> int:
    commands: list[list[str]] = []

    if not args.skip_unit:
        commands.append(list(UNIT_TEST_COMMAND))

    if args.integration:
        commands.append(list(INTEGRATION_TEST_COMMAND))

    if not args.skip_import_smoke:
        commands.append(list(IMPORT_SMOKE_COMMAND))

    for command in commands:
        exit_code = run_command(command)
        if exit_code != 0:
            return exit_code

    print("Dependency validation flow completed successfully.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect, update, and validate dependency changes for this repository."
    )
    parser.set_defaults(handler=lambda _: parser.print_help() or 0)

    subparsers = parser.add_subparsers(dest="command")

    report_parser = subparsers.add_parser(
        "report",
        help="Show requirement constraints, installed versions, and optionally outdated packages.",
    )
    report_parser.add_argument(
        "--files",
        nargs="+",
        default=list(DEFAULT_REQUIREMENT_FILES),
        help="Requirement files to inspect.",
    )
    report_parser.add_argument(
        "--outdated",
        action="store_true",
        help="Ask pip for available upgrades when network/index access is available.",
    )
    report_parser.set_defaults(handler=command_report)

    pin_parser = subparsers.add_parser(
        "pin",
        help="Rewrite an existing requirement entry using an explicit or installed version.",
    )
    pin_parser.add_argument("package", help="Package name to rewrite.")
    pin_parser.add_argument(
        "--version",
        help="Target version. Defaults to the currently installed version in this interpreter.",
    )
    pin_parser.add_argument(
        "--operator",
        choices=(">=", "=="),
        default=">=",
        help="Constraint operator to write back into the requirement file.",
    )
    pin_parser.add_argument(
        "--files",
        nargs="+",
        default=list(DEFAULT_REQUIREMENT_FILES),
        help="Requirement files to update.",
    )
    pin_parser.set_defaults(handler=command_pin)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Run the repository validation flow after a dependency upgrade.",
    )
    validate_parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests in addition to the unit suite.",
    )
    validate_parser.add_argument(
        "--skip-unit",
        action="store_true",
        help="Skip tests/unit.",
    )
    validate_parser.add_argument(
        "--skip-import-smoke",
        action="store_true",
        help="Skip import checks for app.py and src.bot.",
    )
    validate_parser.set_defaults(handler=command_validate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
