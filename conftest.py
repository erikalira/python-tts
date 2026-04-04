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
