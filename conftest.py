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


# Config reads these through os.environ when its own env file does not declare
# them, and `load_dotenv(override=True)` means any test that declares one in a
# tmp .env exports it to the process for every test that follows. So this list
# covers two hazards with one fixture: a developer's real credential leaking in,
# and one test's fixture value leaking into the next.
_LEAK_PRONE_ENV_VARS = (
    # Provider credentials: a test asserting absence would otherwise read the
    # developer's real key, and pytest prints it in a failing diff. That
    # happened once during the Fish Audio work.
    "FISH_AUDIO",
    "FISH_AUDIO_MODEL",
    # Cross-test leakage: a container test declaring these made a later
    # settings test, which asserts their absence, read them from the process.
    "BOT_SPEAK_TOKEN",
    "MAX_TEXT_LENGTH",
    "BOT_RATE_LIMIT_MAX_REQUESTS",
)


@pytest.fixture(autouse=True)
def sanitize_leak_prone_env(monkeypatch):
    """Isolate every test from environment another test or shell may have set.

    Autouse makes the guarantee structural: a new test inherits it instead of
    having to remember a fixture. `monkeypatch.delenv` restores automatically,
    so this composes with the per-module env snapshots rather than fighting
    them, and a test that declares the variable in its own tmp `.env` is
    unaffected because `load_dotenv(override=True)` wins for declared keys.
    """
    for key in _LEAK_PRONE_ENV_VARS:
        monkeypatch.delenv(key, raising=False)
