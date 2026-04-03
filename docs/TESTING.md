# Testing

This guide documents the project's automated test structure and local execution flow.

## Test Strategy

The repository separates test suites by confidence level, execution cost, and environmental dependency.

- Unit tests are the default safety net. They should be fast, deterministic, and runnable across Windows, Ubuntu, WSL, and CI without relying on real external services or OS-specific runtime setup.
- Integration tests validate real integrations such as network-backed providers, platform TTS bindings, or other environment-dependent adapters. They are intentionally explicit and should not be mixed into the default unit workflow.
- Manual validation complements automation when runtime behavior depends on GUI interaction, audio devices, tray behavior, hotkeys, or external platform state that is not practical to stabilize in automated tests.

## Test Types

### Unit tests

Use unit tests when validating:

- pure business logic
- orchestration and branching
- repository and adapter behavior with mocks or fakes
- error handling that can be simulated locally

Unit tests belong under `tests/unit/`.

### Integration tests

Use integration tests when validating:

- real TTS providers such as `gtts`
- platform bindings such as Windows `sapi5` through `pyttsx3`
- filesystem, network, or OS behavior that is intentionally not mocked

Integration tests belong under `tests/integration/`.

### Manual validation

Use manual validation when the change touches:

- desktop startup flow
- GUI rendering and editability
- tray behavior
- hotkey capture
- audible playback behavior on a real machine

Record the manual validation path in the change summary when automation is not sufficient.

## Environment

The local test environment uses `.env` as a source of variables.

- Some desktop app tests and defaults depend on values loaded from `.env`.
- When reproducing failures locally, verify that `.env` is present and matches the expected scenario.
- When a test overrides variables with `monkeypatch`, that override applies only to that test.
- The VS Code Testing panel should use `.env.test` as its dedicated test env file so proxy variables from the host session do not leak into integration tests.
- Pytest temporary files and cache are redirected to `.test-artifacts/` so the repository root stays clean during local runs.

## Running Tests

```powershell
pip install -r requirements-test.txt
python -m pytest tests/unit
```

## Running Integration Tests

Use integration tests explicitly when you want to validate real providers, OS bindings, or network-backed flows.

```powershell
python -m pytest tests/integration
```

## Recommended Execution Flow

For everyday development:

1. Run `tests/unit` first.
2. Run only the relevant desktop or bot slice when iterating on one runtime.
3. Run `tests/integration` only when the change touches real integrations or when you want a higher-confidence validation pass before shipping.

For CI or automation:

- treat `tests/unit` as the default required suite
- add integration suites explicitly only in environments that provide the required dependencies and platform capabilities
- avoid making integration tests look flaky unit tests by keeping them in separate directories and commands

## VS Code Testing Panel

The workspace includes `.vscode/settings.json` configured to:

- run the unit test suite by default
- activate the selected virtual environment in the integrated terminal
- load `.env.test` before test discovery and execution

Use the interpreter that matches your current environment:

- Windows: `.venv\\Scripts\\python.exe`
- Ubuntu / WSL: `.venv/bin/python`

The `.env.test` file clears proxy variables used by some isolated agent sessions, which prevents false network failures in the VS Code Testing panel.

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
- Do not place environment-dependent integration tests under `tests/unit/`.
- Prefer moving an unstable test into `tests/integration/` over weakening the guarantees of the unit suite.
- When introducing a new test category in the future, document its intent, trigger conditions, and execution command in this guide.

## Structure

- `tests/unit/`: unit tests grouped by layer
- `tests/integration/`: environment-dependent integration tests
- `tests/unit/desktop/`: tests for the desktop app internal runtime
- `tests/conftest.py`: shared fixtures and helpers

## Future Categories

If the repository grows, the next categories that make sense are:

- `tests/e2e/`: end-to-end flows that validate full runtime behavior across process boundaries
- `tests/performance/`: timing or throughput checks kept out of default local runs
- `tests/smoke/`: lightweight deployment or startup checks for release validation

Only introduce a new top-level test category when it has a distinct execution profile and ownership model.
