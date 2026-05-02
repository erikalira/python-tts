from pathlib import Path

import pytest

from scripts.utils import dependency_maintenance


def test_validate_command_allows_known_pytest_command():
    command = list(dependency_maintenance.UNIT_TEST_COMMAND)

    dependency_maintenance.validate_command(command)


def test_validate_command_rejects_arbitrary_python_executable(tmp_path: Path):
    fake_python = tmp_path / "python.exe"
    fake_python.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="current repository Python interpreter"):
        dependency_maintenance.validate_command([str(fake_python), "-m", "pytest", "tests/unit"])


def test_validate_command_rejects_unapproved_arguments():
    command = [dependency_maintenance.REPOSITORY_PYTHON, "-m", "pytest", "-k", "desktop"]

    with pytest.raises(ValueError, match="Unsafe command rejected"):
        dependency_maintenance.validate_command(command)


def test_run_command_dispatches_unit_tests(monkeypatch: pytest.MonkeyPatch):
    observed: list[list[str]] = []

    def fake_run() -> int:
        observed.append(list(dependency_maintenance.UNIT_TEST_COMMAND))
        return 0

    monkeypatch.setattr(dependency_maintenance, "run_unit_tests_command", fake_run)

    exit_code = dependency_maintenance.run_command(list(dependency_maintenance.UNIT_TEST_COMMAND))

    assert exit_code == 0
    assert observed == [list(dependency_maintenance.UNIT_TEST_COMMAND)]


def test_rewrite_requirement_lines_preserves_inline_comment(tmp_path: Path):
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text("requests>=2.31.0  # pinned for desktop flow\n", encoding="utf-8")

    changed = dependency_maintenance.rewrite_requirement_lines(
        requirements_file,
        "requests",
        "2.32.0",
        ">=",
    )

    assert changed is True
    assert requirements_file.read_text(encoding="utf-8") == "requests>=2.32.0  # pinned for desktop flow\n"


def test_rewrite_requirement_lines_preserves_environment_marker(tmp_path: Path):
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text(
        'pywin32>=306; platform_system == "Windows"\n',
        encoding="utf-8",
    )

    changed = dependency_maintenance.rewrite_requirement_lines(
        requirements_file,
        "pywin32",
        "307",
        ">=",
    )

    assert changed is True
    assert requirements_file.read_text(encoding="utf-8") == 'pywin32>=307; platform_system == "Windows"\n'


def test_get_outdated_versions_returns_empty_dict_for_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(dependency_maintenance, "run_outdated_command", lambda: "not-json")

    assert dependency_maintenance.get_outdated_versions() == {}
