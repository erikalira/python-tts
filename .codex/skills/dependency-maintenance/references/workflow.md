# Dependency Maintenance Workflow

## Quick start

Inspect current constraints and outdated packages:

```powershell
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py report --outdated
```

Upgrade one package in the environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -U Pillow
```

Write the installed version back into the requirement file:

```powershell
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py pin Pillow --operator >= --files requirements.txt
```

Validate the migration:

```powershell
.\.venv\Scripts\python.exe scripts\utils\dependency_maintenance.py validate
```

## Decision points

- Use `requirements.txt` for runtime dependencies.
- Use `requirements-test.txt` for test-only dependencies.
- Run `validate --integration` when the dependency touches real TTS, HTTP, Discord, or OS-specific behavior.
- Prefer `pip-compile --upgrade-package <package>` when you want more controlled upgrades.
- Prefer `pur -r requirements.txt` only for intentional broad update passes.

## Expectations

- Keep upgrades small and reviewable.
- Do not mix large dependency churn into unrelated feature work without a clear reason.
- Preserve startup behavior for both the Discord bot and Windows desktop app.
