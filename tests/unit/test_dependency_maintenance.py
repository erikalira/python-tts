from pathlib import Path

import pytest

from scripts.utils import dependency_maintenance


def test_validate_command_allows_known_pytest_command():
    command = [dependency_maintenance.REPOSITORY_PYTHON, "-m", "pytest", "tests/unit"]

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
