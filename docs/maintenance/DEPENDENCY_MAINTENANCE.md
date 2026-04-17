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

Recommended maintenance tools:

- `pip-tools`: compile and control upgrades with more discipline
- `pip-audit`: audit installed or declared dependencies for known vulnerabilities
- `pur`: rewrite requirement files to current latest versions when you intentionally want broad updates

Install them only in the working environment used for maintenance:

```powershell
.\.venv\Scripts\python.exe -m pip install pip-tools pip-audit pur
```

## Repository Helper Script

Use the repository helper script for recurring checks:

```powershell
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py report
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py report --outdated
```

The script can also rewrite an existing requirement entry to the version already installed locally:

```powershell
.\.venv\Scripts\python.exe -m pip install -U Pillow
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py pin Pillow --operator >= --files requirements.txt
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
.\.venv\Scripts\python.exe -m pip-audit -r requirements.txt
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

### 3. Upgrade in the environment first

Upgrade the package in `.venv` before editing the requirement files, so you can confirm what was actually installed.

Examples:

```powershell
.\.venv\Scripts\python.exe -m pip install -U Pillow
.\.venv\Scripts\python.exe -m pip install "Pillow>=12.2.0"
```

If you want controlled compilation with `pip-tools`, use:

```powershell
.\.venv\Scripts\python.exe -m pip-compile --upgrade-package pillow
```

If the repository is still using hand-maintained requirement files, prefer updating only the targeted package entry instead of reordering or rewriting the whole file.

### 4. Update the requirement files deliberately

After the environment is on the intended version, write the constraint back to the relevant files.

Examples:

```powershell
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py pin Pillow --operator >= --files requirements.txt
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py pin pytest --operator >= --files requirements-test.txt
```

Operator guidance:

- use `>=` when the project intentionally allows future compatible upgrades at install time
- use `==` when you need reproducibility and want CI/local installs to match exactly

For application repositories, reproducibility is usually stronger with pinned or compiled lock-style outputs. If you stay with plain `requirements.txt`, document why a direct range is acceptable.

### 5. Validate the migration

Always run the default unit suite after changing dependencies:

```powershell
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py validate
```

Run integration tests when the changed dependency affects:

- TTS engines
- HTTP or network behavior
- Discord adapters
- Windows-specific runtime or GUI integration

```powershell
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py validate --integration
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
.\.venv\Scripts\python.exe -m pip-audit -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -U Pillow
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py pin Pillow --operator >= --files requirements.txt
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py validate
```

### Planned maintenance pass

```powershell
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py report --outdated
.\.venv\Scripts\python.exe -m pip list --outdated
.\.venv\Scripts\python.exe -m pip-audit -r requirements.txt
```

Then decide whether to use:

- targeted `pip install -U <package>`
- `pip-compile --upgrade-package <package>`
- `pur -r requirements.txt` for an intentional broad rewrite

## Review Checklist

- Is the package change scoped to the real problem?
- Is the selected version compatible with the repository Python version?
- Did `requirements.txt` or `requirements-test.txt` get updated intentionally?
- Did `tests/unit` pass?
- Were `tests/integration` run when the dependency touches real providers or platform bindings?
- Did import smoke checks for `app.py` and `src.bot` still pass?
- Was manual validation recorded if desktop runtime behavior changed?
