# Testing

This guide documents the project's automated test structure and local execution flow.

## Environment

The local test environment uses `.env` as a source of variables.

- Some desktop app tests and defaults depend on values loaded from `.env`.
- When reproducing failures locally, verify that `.env` is present and matches the expected scenario.
- When a test overrides variables with `monkeypatch`, that override applies only to that test.

## Running Tests

```powershell
pip install -r requirements-test.txt
python -m pytest
```

## Desktop App in `.venv`

To run the desktop app test suite using the local virtual environment:

```powershell
.\.venv\Scripts\python -m pytest tests/unit/desktop -q
```

## Good Practices

- Prefer isolated tests that do not depend on leftovers from previous runs.
- Keep setup explicit and local to the test or to shared fixtures in `tests/conftest.py`.
- Favor temporary or mocked resources over persistent local artifacts when a test needs filesystem, environment, or network-related setup.
- Assert behavior and outcomes that matter to the user or the application flow, not internal implementation details that make refactors harder.
- Keep tests focused and readable so failures explain what regressed quickly.
- When changing shared logic, verify the affected runtime path and consider whether both the Discord bot and Desktop app need coverage.

## Structure

- `tests/unit/`: unit tests grouped by layer
- `tests/unit/desktop/`: tests for the desktop app internal runtime
- `tests/conftest.py`: shared fixtures and helpers
