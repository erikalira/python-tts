# Testing

This guide documents the project's automated test structure and local execution flow.

## Test Strategy

The repository separates test suites by confidence level, execution cost, and environmental dependency.

- Unit tests are the default safety net. They should be fast, deterministic, and runnable across Windows, Ubuntu, WSL, and CI without relying on real external services or OS-specific runtime setup.
- Integration tests validate real integrations such as network-backed providers, platform TTS bindings, or other environment-dependent adapters. They are intentionally explicit and should not be mixed into the default unit workflow.
- Manual validation complements automation when runtime behavior depends on GUI interaction, audio devices, tray behavior, hotkeys, or external platform state that is not practical to stabilize in automated tests.
- Smoke tests provide lightweight release gates for startup and minimum-path validation across the bot and desktop runtimes.

## Test Types

### Unit tests

Use unit tests when validating:

- pure business logic
- orchestration and branching
- extracted application collaborators such as resolvers and orchestrators
- presenter and mapper behavior per transport
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

### Smoke tests

Use smoke tests when validating:

- bot startup wiring and operational endpoints such as `GET /health`
- desktop startup and the minimum supported runtime flow
- release-gate checks that should stay lightweight and fast

Smoke tests belong under `tests/smoke/`.

## Environment

The local test environment uses `.env` as a source of variables.

- Some desktop app tests and defaults depend on values loaded from `.env`.
- When reproducing failures locally, verify that `.env` is present and matches the expected scenario.
- When a test overrides variables with `monkeypatch`, that override applies only to that test.
- The VS Code Testing panel should use `.env.test` as its dedicated test env file so proxy variables from the host session do not leak into integration tests.
- Pytest temporary files and cache are redirected to `.test-artifacts/` so the repository root stays clean during local runs.

## Running Tests

Prefer using the repository virtual environment directly instead of relying on a globally installed `pytest`.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit
```

If the `.venv` has not been prepared yet, install the test dependencies there first:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-test.txt
```

## Running Integration Tests

Use integration tests explicitly when you want to validate real providers, OS bindings, or network-backed flows.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/integration
```

To run only the Redis-backed integration suite against a real Redis instance:

```powershell
$env:RUN_REDIS_INTEGRATION_TESTS="1"
$env:REDIS_HOST="127.0.0.1"
$env:REDIS_PORT="6379"
$env:REDIS_DB="15"
.\.venv\Scripts\python.exe -m pytest tests/integration/infrastructure/test_audio_queue_redis_integration.py tests/integration/bot_runtime/test_queue_worker_redis_integration.py
```

## Running Smoke Tests

Use smoke tests explicitly when you want a release-style startup validation pass.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/smoke
```

## Recommended Execution Flow

For everyday development:

1. Run `tests/unit` first.
2. Run only the relevant desktop or bot slice when iterating on one runtime.
3. Prefer the narrowest layer-focused suite when refactoring shared code, for example `tests/unit/application/` or `tests/unit/presentation/`.
4. Run `tests/integration` only when the change touches real integrations or when you want a higher-confidence validation pass before shipping.

For CI or automation:

- treat `tests/unit` plus `tests/smoke` as the default required cross-platform suite
- run mandatory lint and type-check gates before the critical test suite
- keep the critical suite running on both Linux and Windows
- keep the global coverage gate at `80%` or higher and raise it gradually toward the `85%` target once the suite supports it
- enforce dedicated coverage gates for the critical `queue` and `runtime_observability` domains instead of relying only on one repository-wide percentage
- keep Redis-backed integration coverage in a dedicated CI job with a real Redis service
- add integration suites explicitly only in environments that provide the required dependencies and platform capabilities
- keep network- and OS-dependent integrations in separate CI jobs so they do not blur the default local developer workflow
- avoid making integration tests look flaky unit tests by keeping them in separate directories and commands

Static quality gates:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pyright
```

`ruff` currently enforces high-signal correctness rules such as syntax and
undefined-name failures. `pyright` is intentionally scoped in
`pyrightconfig.json` to typed contracts, core interfaces, and quality-gate
helpers. Expand the checked surface area as modules become type-clean instead
of disabling the gate when legacy typing gaps appear.

To validate the repository quality gates against an existing `coverage.xml`:

```powershell
.\.venv\Scripts\python.exe scripts/test/quality_gates.py coverage --coverage-xml coverage.xml --config config/quality_gates.json
```

The release-gate smoke suite also checks the bot observability baseline against
the configured SLI thresholds in `config/quality_gates.json`.

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
.\.venv\Scripts\python.exe -m pytest tests/unit/desktop -q
```

## Good Practices

- Prefer isolated tests that do not depend on leftovers from previous runs.
- Keep setup explicit and local to the test or to shared fixtures in `tests/conftest.py`.
- Use shared builders in `tests/conftest.py` for composition-heavy flows so refactors update one place instead of every test.
- Favor temporary or mocked resources over persistent local artifacts when a test needs filesystem, environment, or network-related setup.
- Assert behavior and outcomes that matter to the user or the application flow, not internal implementation details that make refactors harder.
- Keep tests focused and readable so failures explain what regressed quickly.
- When changing shared logic, verify the affected runtime path and consider whether both the Discord bot and Desktop app need coverage.
- When logic is extracted into a dedicated application or presentation collaborator, add or move tests so that collaborator has its own focused test file.
- Do not place environment-dependent integration tests under `tests/unit/`.
- Prefer moving an unstable test into `tests/integration/` over weakening the guarantees of the unit suite.
- When introducing a new test category in the future, document its intent, trigger conditions, and execution command in this guide.

## Structure

- `tests/unit/`: unit tests grouped by layer
- `tests/unit/application/`: use cases plus extracted shared collaborators such as resolvers and queue orchestrators
- `tests/unit/presentation/`: controllers, commands, and transport presenters
- `tests/integration/`: environment-dependent integration tests
- `tests/smoke/`: lightweight startup and minimum-flow release checks
- `tests/unit/desktop/`: tests for the desktop app internal runtime
- `tests/conftest.py`: shared fixtures and helpers

## Future Categories

If the repository grows, the next categories that make sense are:

- `tests/e2e/`: end-to-end flows that validate full runtime behavior across process boundaries
- `tests/performance/`: timing or throughput checks kept out of default local runs
- `tests/smoke/`: lightweight deployment or startup checks for release validation

Only introduce a new top-level test category when it has a distinct execution profile and ownership model.
