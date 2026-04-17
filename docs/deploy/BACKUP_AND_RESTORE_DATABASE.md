# Backup And Restore Database

This guide documents how to back up and restore the Dockerized Postgres
database used by the Discord bot.

It is written to be practical for a Windows server, but the same database
strategy also applies on Linux:

- keep Postgres data in a persistent Docker volume
- generate logical backups with `pg_dump`
- restore with `pg_restore`
- store backups outside the container

## Recommended strategy

Do not back up the raw Postgres container filesystem as your primary process.
Use logical backups instead.

Recommended baseline:

1. Postgres runs in Docker with a persistent volume
2. backups are generated with `pg_dump -Fc`
3. backup files are stored on the host machine
4. the host backup folder is synced or copied elsewhere
5. restores are tested periodically

## Windows server flow

Suggested folder:

```text
C:\Backups\tts-bot\
```

If Google Drive is installed on the server, the simplest professional setup is:

1. choose a backup folder inside a Google Drive synced path, or
2. back up locally and let Google Drive sync that folder

Important:

- sync the generated `.dump` files
- do not sync the live Docker volume directory as your primary backup method

## Provided scripts

This repository includes:

- `scripts/utils/backup_postgres.ps1`
- `scripts/utils/restore_postgres.ps1`

### Backup

Example:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/utils/backup_postgres.ps1 `
  -ContainerName tts-bot-postgres `
  -DatabaseName tts_hotkey_windows `
  -DatabaseUser your_postgres_user `
  -BackupDirectory "C:\Backups\tts-bot" `
  -RetentionDays 30
```

What it does:

- creates a timestamped `.dump` file using `pg_dump -Fc`
- copies the backup from the container to the host
- removes the temporary file inside the container
- deletes local backups older than the chosen retention window

### Restore

Example:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/utils/restore_postgres.ps1 `
  -BackupFile "C:\Backups\tts-bot\tts_backup_2026-04-13_03-00-00.dump" `
  -ContainerName tts-bot-postgres `
  -DatabaseName tts_hotkey_windows `
  -DatabaseUser your_postgres_user
```

What it does:

- copies the selected backup file into the Postgres container
- restores it with `pg_restore --clean --if-exists`
- removes the temporary file inside the container

## Suggested production routine

For a small but serious deployment:

- run backup once per day
- keep 14 to 30 daily backups locally
- sync the backup folder with Google Drive
- test restore at least occasionally

If the data volume grows in importance later, you can expand this to:

- more frequent backups
- weekly offline copies
- restore verification on a staging database

## Task Scheduler on Windows

Recommended approach:

1. open Task Scheduler
2. create a new task
3. schedule it daily during low usage hours, for example `03:00`
4. action:

```text
powershell.exe
```

Arguments:

```text
-ExecutionPolicy Bypass -File "C:\path\to\repo\scripts\utils\backup_postgres.ps1" -BackupDirectory "C:\Backups\tts-bot" -RetentionDays 30
```

## Linux note

On Linux, the same backup model still applies. The operational difference is
usually just scheduling with `cron` or `systemd timers` instead of Windows Task
Scheduler.

The database backup and restore commands themselves are the same in principle:

- `pg_dump -Fc` for backup
- `pg_restore` for restore

## Recovery expectations

For this project today, the database mainly stores bot configuration. That
means restore is operationally important, but not as complex as restoring a
high-write transactional system.

That said, the professional habit is still:

- keep backups versioned
- keep at least one copy off the live machine
- confirm restore works before trusting the process
