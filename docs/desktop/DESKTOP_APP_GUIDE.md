# Desktop App Guide

This guide summarizes the operational view of the Windows Desktop App.

## Entry Points

- local execution: `app.py`
- internal runtime: `src/desktop/`
- composition root: `src/desktop/app/bootstrap.py`

## Configuration

Use the persisted Desktop App configuration in `src/desktop/config/desktop_config.py`
and the app's own graphical interface to adjust Discord, TTS, hotkeys, and UI preferences.

The Desktop App's main flow is to send captured text to the Discord bot.
The local Windows voice path with `pyttsx3` remains available only as an optional
accessibility/fallback feature and is disabled by default.

### Discord ID

The Desktop App can use the user ID to discover which voice channel you are in.

To copy that ID in Discord:

1. Open `User Settings`
2. Under `Advanced`, enable `Developer Mode`
3. Right-click your name in any chat
4. Choose `Copy User ID`
5. Paste the value into the app configuration interface

### Hotkeys

Prefer key combinations that:

- do not conflict with Windows global shortcuts
- do not conflict with common editor, browser, Discord, or OBS shortcuts
- are easy to remember
- are comfortable for opening and closing capture

If your configuration uses an opening key and a closing key, choose a pair that
is easy to recognize while typing.

The default usage flow is:

1. join a Discord voice channel
2. open the Desktop App
3. press the opening hotkey
4. type the text
5. press the closing hotkey
6. let the text go to the bot

When the app depends on the bot for speech, it uses this priority order to discover the channel:

1. already connected channel, if you used `/join` before
2. user ID lookup to locate the current voice channel
3. error if no strategy works

## Environment

The local project environment is based on `.env`.

- the Desktop App uses `.env` as a source for environment variables and defaults
- persisted configuration values can coexist with variables defined in `.env`
- keep `.env` configured to reproduce local behavior and test scenarios

## Main Panel

When the executable opens, the user sees a main panel that:

- stays open as the app's main window
- allows Discord, TTS, hotkey, and UI preference configuration
- makes it explicit when the optional local Windows voice path is enabled
- offers an on-demand `Test connection` action without continuous polling
- offers a manual `Send voice test` action with a short message
- shows useful activity and logs without depending on the terminal

## UX Guidelines

The Desktop App should preserve a predictable end-user experience:

- the interface should remain responsive during common interactions
- GUI handlers should not block the main thread with long-running work
- editable fields should reliably accept focus, selection, typing, and paste
- read-only or disabled states should be visually clear
- the main window should guide the initial flow without depending on the terminal
- minimize, restore, and exit should follow a consistent flow
- the GUI should collect data and delegate actions without absorbing business rules

## Build

```powershell
python app.py
./scripts/build/build_clean_architecture.ps1
```

## Related

- [../architecture/ARCHITECTURE.md](../architecture/ARCHITECTURE.md)
- [../architecture/BOT_DESKTOP_HTTP_CONTRACT.md](../architecture/BOT_DESKTOP_HTTP_CONTRACT.md)
