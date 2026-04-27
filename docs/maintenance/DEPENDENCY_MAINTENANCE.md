# Dependency Maintenance

This guide defines the repository workflow for checking dependency health, updating packages, and validating that the migration did not break either application mode.

Use this guide when:

- Codacy or another scanner reports a vulnerable package
- a package needs to be upgraded for compatibility or bug fixes
- you want a repeatable workflow instead of ad-hoc `pip install -U`

## Goals

- keep dependency upgrades small and reviewable
- avoid changing multiple packages without a clear reason
- preserve independent execution of the Discord bot and Windows desktop app
- validate the migration with tests and startup smoke checks

## Tooling

Prefer using the project virtual environment directly.

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
```

Primary maintenance tools:

- `uv`: resolve dependencies and maintain `uv.lock`
- `pip-audit`: audit declared dependencies for known vulnerabilities
- CycloneDX tooling: generate SBOMs for supply-chain traceability

Install and sync them through the repository virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install uv==0.11.3
uv sync --locked --group test --group security
```

The repository also runs automated supply-chain gates in GitHub Actions:

- Dependabot opens weekly PRs for `uv.lock` and GitHub Actions.
- `Security` runs `pip-audit` for `requirements.txt` and `requirements-test.txt`
  using tooling installed from the locked `security` dependency group.
- PRs run GitHub dependency review when dependency manifests change.
- CodeQL scans Python on PRs, pushes to `main`, scheduled runs, and manual dispatch.

## Repository Helper Script

Use the repository helper script for recurring checks:

```powershell
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py report
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py report --outdated
```

The script can also rewrite an existing requirement entry to the version already installed locally:

```powershell
uv add "Pillow>=12.2.0"
uv lock
```

After an upgrade, validate the migration:

```powershell
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py validate
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py validate --integration
```

## Recommended Upgrade Workflow

### 1. Inspect the current state

Check declared constraints, installed versions, and possible upgrades.

```powershell
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py report --outdated
.\.venv\Scripts\python.exe -m pip list --outdated
uv run --group security pip-audit -r requirements.txt
```

When the issue is security-driven, read the advisory before upgrading. Confirm whether the fix requires:

- a minimum safe version
- the latest version
- a major-version migration with breaking changes

Do not upgrade to the absolute latest version blindly if the release notes or Python compatibility say otherwise.

### 2. Choose the upgrade style

Use one of these approaches:

- Single-package security or compatibility fix: upgrade only the affected package first.
- Small related batch: upgrade a tightly related group only when they are coupled in practice.
- Broad maintenance pass: reserve for dedicated dependency-update work, not feature implementation.

For day-to-day implementation work, prefer the smallest package set that resolves the problem.

Keep `requirements.txt` and `requirements-test.txt` as temporary compatibility
files while deployment paths finish moving to `uv.lock`. Add new dependencies to
`pyproject.toml` first, then run `uv lock`.

### 3. Upgrade in the environment first

Update the project metadata first, then let `uv` resolve the exact environment.

Examples:

```powershell
uv add "Pillow>=12.2.0"
uv lock
uv sync --locked --group test
```

For dependency groups:

```powershell
uv add --group test "pytest>=9.0.3"
uv add --group build "pyinstaller>=5.0"
uv add --group security "pip-audit>=2.9.0"
```

If the repository is still using hand-maintained requirement files, prefer updating only the targeted package entry instead of reordering or rewriting the whole file.

### 4. Update the requirement files deliberately

After the lockfile is updated, update compatibility requirements only when a
remaining deployment path still consumes them. The steady state is
`pyproject.toml` plus `uv.lock`.

### 5. Validate the migration

Always run the default unit suite after changing dependencies:

```powershell
uv run pytest tests/unit
uv run pytest tests/smoke
```

Run integration tests when the changed dependency affects:

- TTS engines
- HTTP or network behavior
- Discord adapters
- Windows-specific runtime or GUI integration

```powershell
uv run pytest tests/integration
```

Also verify the affected runtime path directly when automation is not enough:

- Discord bot startup assumptions
- desktop app startup and hotkey flow
- tray, GUI, and audible playback when desktop dependencies changed

## Best Practices

- Separate dependency-only changes from feature changes whenever practical.
- Upgrade one risky package at a time when a major version is involved.
- Read release notes for major versions and Python version support before merging.
- Prefer writing the requirement file from the environment that actually passed validation.
- Record any manual validation performed when desktop or OS-specific behavior is involved.
- If an upgrade requires code changes, keep those code changes small and focused on compatibility.
- Re-run `pip-audit` after the migration when the trigger was a security advisory.

## Suggested Commands By Scenario

### Vulnerability in one package

```powershell
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py report --outdated
uv run --group security pip-audit -r requirements.txt
uv add "Pillow>=12.2.0"
uv lock
uv sync --locked --group test --group security
uv run pytest tests/unit tests/smoke --tb=short -v
```

### Planned maintenance pass

```powershell
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py report --outdated
.\.venv\Scripts\python.exe -m pip list --outdated
uv run --group security pip-audit -r requirements.txt
```

Then decide whether to use:

- targeted `uv add` for one dependency
- `uv lock --upgrade-package <package>` for a controlled lockfile upgrade
- `uv lock --upgrade` for an intentional broad update pass

## Review Checklist

- Is the package change scoped to the real problem?
- Is the selected version compatible with the repository Python version?
- Did `pyproject.toml` and `uv.lock` get updated intentionally?
- If a compatibility requirements file changed, is the temporary need clear?
- Did `tests/unit` pass?
- Were `tests/integration` run when the dependency touches real providers or platform bindings?
- Did import smoke checks for `app.py` and `src.bot` still pass?
- Was manual validation recorded if desktop runtime behavior changed?
- Did the `Security` workflow pass, including `pip-audit`, dependency review,
  and CodeQL when applicable?
