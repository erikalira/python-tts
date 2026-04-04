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

    class Completed:
        returncode = 0

    def fake_run() -> Completed:
        observed.append(list(dependency_maintenance.UNIT_TEST_COMMAND))
        return Completed()

    monkeypatch.setattr(dependency_maintenance, "run_unit_tests_command", fake_run)

    exit_code = dependency_maintenance.run_command(list(dependency_maintenance.UNIT_TEST_COMMAND))

    assert exit_code == 0
    assert observed == [list(dependency_maintenance.UNIT_TEST_COMMAND)]
