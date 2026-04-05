# Windows Bot Service with WinSW

This guide documents the recommended way to keep the Discord bot running on a Windows server by wrapping `python -m src.bot` as a Windows service with WinSW.

Use this guide only for the Discord bot runtime. The Desktop App remains a separate application and should not be installed as a Windows service.

## Why WinSW

For this repository, WinSW is a good fit because:

- it wraps a normal Python process as a Windows service
- it starts automatically with Windows
- it can restart the bot after failures
- it keeps service logs in a predictable location
- it does not require changing the bot architecture or entrypoint

The bot runtime already starts through [`src/bot.py`](../src/bot.py), so the service only needs to launch the existing command:

```powershell
python -m src.bot
```

## Recommended server layout

Avoid running the service from a user Desktop folder on the server. A dedicated service path is more stable and easier to maintain.

Suggested layout:

```text
C:\services\tts-hotkey-windows\
|-- .venv\
|-- .env
|-- deploy\
|   \-- winsw\
|       |-- tts-discord-bot.exe
|       |-- tts-discord-bot.xml
|       \-- logs\
|-- src\
|-- requirements.txt
|-- app.py
```

## Prerequisites

Before installing the service:

1. Clone or copy the repository to the server.
2. Create the virtual environment in the repository root.
3. Install Python dependencies into `.venv`.
4. Install `ffmpeg` and confirm it is available in the service account `PATH`.
5. Create the production `.env` file in the repository root.

Setup references:

- [SETUP.md](SETUP.md)
- [ENVIRONMENTS.md](ENVIRONMENTS.md)

Minimum `.env` for a Windows-hosted bot:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
DISCORD_BOT_HOST=0.0.0.0
DISCORD_BOT_PORT=10000
```

If the Windows service account cannot resolve `ffmpeg` from `PATH`, set an explicit path in `.env`:

```env
FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe
```

If the Desktop App will connect to this server from another machine, make sure:

- the Windows firewall allows inbound access to the configured bot port
- `DISCORD_BOT_HOST` is `0.0.0.0`
- the Desktop App uses the reachable server URL in `DISCORD_BOT_URL`

## WinSW files

This repository includes a ready-to-use WinSW XML template:

- [`deploy/winsw/tts-discord-bot.xml`](../deploy/winsw/tts-discord-bot.xml)
- [`deploy/winsw/install-or-update-service.ps1`](../deploy/winsw/install-or-update-service.ps1)
- [`deploy/winsw/.env.windows-server.example`](../deploy/winsw/.env.windows-server.example)

The template assumes:

- the repository root contains `.venv`
- the WinSW executable and XML live in `deploy/winsw/`
- the bot should run with `python -m src.bot`

The PowerShell helper script assumes the same layout and can install or refresh the service on the server.

## Install steps

### 1. Download WinSW

Download the current WinSW executable from the official releases page and place it in:

```text
deploy\winsw\tts-discord-bot.exe
```

Official source:

- https://github.com/winsw/winsw/releases

The executable must sit next to the XML file and use the same base name:

- `tts-discord-bot.exe`
- `tts-discord-bot.xml`

### 2. Copy the XML template

Keep the repository template in place or copy it beside the executable:

```text
deploy\winsw\tts-discord-bot.xml
```

The checked-in template already points to:

- `%BASE%\..\..\.venv\Scripts\python.exe`
- `%BASE%\..\..` as the working directory

That matches the recommended folder layout above.

### 2.5. Prepare the server `.env`

Use the repository example as the starting point:

```text
deploy\winsw\.env.windows-server.example
```

On the server, copy its contents into:

```text
.env
```

Then replace `YOUR_DISCORD_BOT_TOKEN` with the real token and adjust any optional values you need.

### 3. Optional: run with a dedicated service account

By default, WinSW installs the service using the Windows default service account behavior. For production, prefer a dedicated low-privilege local user or service account.

If you want that, edit [`deploy/winsw/tts-discord-bot.xml`](../deploy/winsw/tts-discord-bot.xml) and uncomment the `<serviceaccount>` block.

That account should have:

- read and execute access to the repository
- access to `.venv\Scripts\python.exe`
- access to `ffmpeg`
- permission to log on as a service

### 4. Install the service

Open an elevated PowerShell in the repository root and run:

```powershell
cd deploy\winsw
.\tts-discord-bot.exe install
.\tts-discord-bot.exe start
```

Or use the helper script to install dependencies and install or refresh the service in one step:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\winsw\install-or-update-service.ps1
```

Useful commands:

```powershell
.\tts-discord-bot.exe status
.\tts-discord-bot.exe stop
.\tts-discord-bot.exe restart
.\tts-discord-bot.exe refresh
.\tts-discord-bot.exe uninstall
```

## Logs

The template writes logs to:

```text
deploy\winsw\logs\
```

Check this directory first when the service fails to start or keeps restarting.

You should expect to see wrapper logs plus the Python process output captured by WinSW.

## Validation checklist

After installation, validate the bot path directly:

1. Confirm the Windows service status is `Running`.
2. Confirm the bot logs show Discord login success.
3. Confirm the configured HTTP port is listening.
4. From the server, call the health endpoint if applicable to your deployment flow.
5. If the Desktop App will use this server, test one real request from the Desktop App against the server URL.

Repository-specific reminder:

- validate the Discord bot runtime after service setup
- do not treat the Desktop App as covered by that check; it remains independent

## Updating the bot

Updating `main` in the remote Git repository does not update the server by itself.

WinSW keeps the bot process running, but it does not:

- pull new commits from Git
- update `.venv` dependencies
- restart the service after code changes unless you tell it to

For the server to receive a new version, some deployment step must happen on the server itself. That can be manual, scheduled, or automated by CI/CD.

For a normal update:

```powershell
cd deploy\winsw
.\tts-discord-bot.exe stop
```

Then:

1. update the repository files
2. update dependencies in `.venv` if needed
3. update `.env` if required
4. run `.\tts-discord-bot.exe start`

If you change service metadata in the XML, run:

```powershell
.\tts-discord-bot.exe refresh
```

If you want the standard manual update path, use:

```powershell
git pull
powershell -ExecutionPolicy Bypass -File .\deploy\winsw\install-or-update-service.ps1
```

## Does it auto-update when `main` changes?

No. A new commit on `origin/main` does nothing on the server until the server runs a deployment action such as:

- `git pull` manually
- a scheduled PowerShell task that pulls and restarts the service
- a CI/CD pipeline that deploys to the server
- a webhook-driven deployment process

If you want automatic updates later, the safest next step is usually a small scheduled task or CI/CD job that:

1. pulls the repository
2. installs updated dependencies when needed
3. refreshes or restarts the WinSW service

For now, the repository is prepared for a manual server deployment flow.

## Production flow with GitHub Actions Runner

If you want automatic deploys on Windows Server, the recommended setup for this repository is:

1. Install WinSW on the server to run the bot as a Windows service.
2. Install a self-hosted GitHub Actions Runner on the same server.
3. Keep the repository checked out at `C:\services\tts-hotkey-windows`.
4. Label the runner with `self-hosted`, `windows`, and `bot-server`.
5. Let GitHub Actions run the deploy workflow on every push to `main`.

The repository now includes the workflow:

- [`.github/workflows/deploy-bot-windows.yml`](../.github/workflows/deploy-bot-windows.yml)

That workflow does this:

1. runs the test suite on GitHub-hosted Linux infrastructure
2. waits for tests to pass
3. runs the deploy job on the self-hosted Windows runner
4. executes `git pull --ff-only origin main` on the server
5. runs `deploy\winsw\install-or-update-service.ps1`
6. checks that the `tts-discord-bot` Windows service is running

Important:

- the workflow assumes the repository lives at `C:\services\tts-hotkey-windows`
- the workflow assumes the runner has Git, Python, and access to the existing `.venv`
- the workflow assumes `tts-discord-bot.exe` already exists in `deploy\winsw\`

This gives you the clean split:

- WinSW keeps the bot alive as an OS-managed service
- GitHub Actions Runner performs code updates and service refreshes

## Troubleshooting

### Service starts and immediately stops

Usually this means one of these:

- `DISCORD_TOKEN` is missing in `.env`
- `.venv` is missing or the Python path is wrong
- `ffmpeg` is not available for the service account
- the account running the service cannot read the repository path

### Service works manually but not as a Windows service

This usually points to an environment difference between your shell and the service account:

- different `PATH`
- different file permissions
- missing access to `.env`
- missing access to `ffmpeg`

If `ffmpeg` works in your user terminal but not in the service, set `FFMPEG_PATH` in the repository root `.env` and restart the service.

### Bot HTTP API is not reachable from another machine

Check:

- `DISCORD_BOT_HOST=0.0.0.0`
- the configured port is open in Windows Firewall
- the server address used by the Desktop App is reachable on the network

## Notes

- Keep secrets only in `.env` or another secure secret source, never in the WinSW XML file.
- Keep the bot service deployment separate from the Desktop App runtime.
- If the server path differs from the recommended layout, update the XML paths before installing the service.
