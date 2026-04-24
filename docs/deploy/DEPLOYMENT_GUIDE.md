# Deployment Guide

Use this guide as the entrypoint when you want to deploy the Discord bot on a
server.

The repository supports more than one deployment shape, so the right document
depends on what you are trying to do.

## Quick chooser

### I want the simplest Windows Server deploy

Use:

- [WINDOWS_BOT_DEPLOY.md](WINDOWS_BOT_DEPLOY.md)

Choose this when:

- the server is Windows
- you want the bot to run as a Windows service
- you are using WinSW to keep `python -m src.bot` alive

You will probably also need:

- [ENVIRONMENTS.md](ENVIRONMENTS.md)

## I want Docker plus Postgres

Use:

- [DOCKER_POSTGRES_DEPLOY.md](DOCKER_POSTGRES_DEPLOY.md)

Choose this when:

- you want the bot packaged in Docker
- you want to use the repository's bundled Docker Compose flow
- you want Postgres as the bot's config storage backend

You will probably also need:

- [ENVIRONMENTS.md](ENVIRONMENTS.md)
- [BOT_PRODUCTION_PERSISTENCE.md](BOT_PRODUCTION_PERSISTENCE.md)
- [BACKUP_AND_RESTORE_DATABASE.md](BACKUP_AND_RESTORE_DATABASE.md)
- [STAGING_AND_ROLLBACK.md](STAGING_AND_ROLLBACK.md)
- [../operations/PRODUCTION_RUNBOOKS.md](../operations/PRODUCTION_RUNBOOKS.md)
- [../operations/DR_DRILLS.md](../operations/DR_DRILLS.md)
- [../operations/RELEASE_CHECKLIST.md](../operations/RELEASE_CHECKLIST.md)

## I want only local Postgres

Use:

- [DOCKER_POSTGRES_DEPLOY.md](DOCKER_POSTGRES_DEPLOY.md#21-local-postgres-only)

Choose this when:

- you want to run `python -m src.bot` locally
- you want Postgres persistence instead of JSON config files
- you do not want to start Redis, Grafana, Prometheus, Tempo, or the bot container

## I want to understand the recommended production architecture first

Use:

- [BOT_PRODUCTION_PERSISTENCE.md](BOT_PRODUCTION_PERSISTENCE.md)

Choose this when:

- you are deciding between JSON and Postgres
- you want to understand the recommended persistence baseline
- you are planning future production growth

## I only need environment variables

Use:

- [ENVIRONMENTS.md](ENVIRONMENTS.md)

Choose this when:

- you already know the deployment shape
- you just need the required `.env` values
- you want to confirm bot vs desktop environment differences

## I need backup and restore for the database

Use:

- [BACKUP_AND_RESTORE_DATABASE.md](BACKUP_AND_RESTORE_DATABASE.md)

Choose this when:

- you are operating the Dockerized Postgres flow
- you need recovery procedure and retention guidance

## I need production runbooks or release operations

Use:

- [../operations/PRODUCTION_RUNBOOKS.md](../operations/PRODUCTION_RUNBOOKS.md)
- [../operations/DR_DRILLS.md](../operations/DR_DRILLS.md)
- [../operations/RELEASE_CHECKLIST.md](../operations/RELEASE_CHECKLIST.md)

Choose these when:

- the bot is deployed with Redis, Postgres, health checks, and restart policy
- you need incident procedures for lock starvation, stuck queues, or engine degradation
- you need to rehearse Postgres restore, Redis recovery, or version rollback
- you need the production release checklist for bot and desktop validation

## I need staging or rollback guidance

Use:

- [STAGING_AND_ROLLBACK.md](STAGING_AND_ROLLBACK.md)

Choose this when:

- you are preparing a production release
- you need staging validation before deploy
- you need to define or execute a rollback point

## Recommended reading order

If you are still unsure, read in this order:

1. [ENVIRONMENTS.md](ENVIRONMENTS.md)
2. one primary deploy guide:
   - [WINDOWS_BOT_DEPLOY.md](WINDOWS_BOT_DEPLOY.md), or
   - [DOCKER_POSTGRES_DEPLOY.md](DOCKER_POSTGRES_DEPLOY.md)
3. [BOT_PRODUCTION_PERSISTENCE.md](BOT_PRODUCTION_PERSISTENCE.md) when making
   production decisions
4. [BACKUP_AND_RESTORE_DATABASE.md](BACKUP_AND_RESTORE_DATABASE.md) if Postgres
   backup/recovery matters for your setup
5. [../operations/RELEASE_CHECKLIST.md](../operations/RELEASE_CHECKLIST.md)
   before each production release
6. [STAGING_AND_ROLLBACK.md](STAGING_AND_ROLLBACK.md) before promoting a
   release to production
7. [../operations/PRODUCTION_RUNBOOKS.md](../operations/PRODUCTION_RUNBOOKS.md)
   and [../operations/DR_DRILLS.md](../operations/DR_DRILLS.md) before the
   stack handles production traffic

## Important scope note

This deployment guidance is for the Discord bot runtime.

The Desktop App is a separate application and should not be treated as part of
the server deployment flow.
