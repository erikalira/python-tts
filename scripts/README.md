# Scripts Directory

This directory contains build, manual test, and utility scripts for the Desktop
App and bot operations.

## Windows Build

```powershell
# Recommended build flow
powershell scripts/build/build_clean_architecture.ps1
```

The executable is created at `dist/HotkeyTTS.exe`.

## Included Capabilities

- Standard developer command wrapper through `scripts/dev.ps1`
- Clean Architecture build flow
- Tkinter GUI
- System tray and notifications
- Multi-engine TTS (`gTTS` + `pyttsx3`)
- Persistent configuration in `AppData/Local/DesktopApp/`
- Global hotkeys
- Single Desktop App entry point

## Utilities

- `create_icon.py`: generates executable icons
- `backup_postgres.ps1`: creates a logical Postgres backup from the container
  with local retention
- `restore_postgres.ps1`: restores a `.dump` backup into the Postgres container
- `dependency_maintenance.py`: inspects package versions, rewrites
  `requirements*.txt` constraints, and runs post-migration validation
- `migrate_json_config_to_postgres.py`: migrates bot `guild_*.json` configs to
  the Postgres backend

## Manual Checks

- `scripts/test/manual_integration_check.py`: manual integration and dependency
  smoke check
- `scripts/test/manual_security_check.py`: manual validation for the bot
  security scenario
- `scripts/test/test_discord_connection.py`: manual Desktop App to Discord bot
  connection check using `DISCORD_BOT_URL`

## Requirements

### Build Scripts

- `PowerShell` (`pwsh` or `powershell`)
- `uv`
- Build dependencies: `uv sync --locked --group build`

### Test Scripts

- `uv sync --locked --group test`
- `Python 3.11+`
- Required environment variables for the flow being tested

## Quick Commands

```powershell
# Install test dependencies
.\scripts\dev.ps1 sync

# Daily validation
.\scripts\dev.ps1 ci

# Desktop App focus
uv run --group test pytest tests/unit/desktop

# Windows executable build
.\scripts\build\build_clean_architecture.ps1
```

## CI/CD Integration

The scripts are intended to work locally and in CI/CD environments:

- GitHub Actions: use `scripts/build/build_clean_architecture.ps1`
- Local development: use `scripts/dev.ps1`
- Windows: use PowerShell for builds
- Linux/macOS: use Python for development and the Windows workflow to build the
  `.exe`

## Troubleshooting

### PowerShell Not Found

```bash
# Ubuntu/Debian
sudo apt install powershell

# macOS
brew install powershell
```

### Linux Permissions

```bash
chmod +x scripts.sh
chmod +x scripts/test/*.sh
```

### Dependency Errors

```powershell
uv sync --locked --all-groups
uv pip list
```

## Contributing

When adding scripts:

1. Add them under `scripts/build/`, `scripts/test/`, or `scripts/utils/`.
2. Update this README.
3. Update related documentation when needed.

## Useful Links

- [Main README](../README.md)
- [Architecture](../docs/architecture/ARCHITECTURE.md)
- [Desktop App Guide](../docs/desktop/DESKTOP_APP_GUIDE.md)
