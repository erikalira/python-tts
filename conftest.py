import shutil
import uuid
from pathlib import Path

import pytest

_TMP_ROOT = Path(".test-artifacts") / "tmp"


@pytest.fixture
def tmp_path():
    """Provide a stable workspace-local tmp path on Windows without pytest tempdir internals."""
    _TMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = _TMP_ROOT / f"pytest-{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


_PROVIDER_CREDENTIAL_ENV_VARS = ("FISH_AUDIO", "FISH_AUDIO_MODEL")


@pytest.fixture(autouse=True)
def sanitize_provider_credentials(monkeypatch):
    """Keep a developer's real provider credentials out of every test.

    `Config` falls back to `os.environ`, so a test that asserts on a variable its
    own tmp `.env` does not declare would read the real value - and pytest prints
    it in the comparison diff when the assertion fails. That happened once during
    the Fish Audio work. Autouse here makes the guarantee structural: a new test
    for a new provider inherits it instead of having to remember a fixture.
    """
    for key in _PROVIDER_CREDENTIAL_ENV_VARS:
        monkeypatch.delenv(key, raising=False)
