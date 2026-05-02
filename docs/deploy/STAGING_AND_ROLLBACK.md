# Staging And Rollback

Use this guide when promoting the Docker production stack through staging and
when rolling back a bad release.

## Application Versioning

The production compose file identifies the bot image with:

```env
BOT_IMAGE=tts-hotkey-windows-bot
APP_VERSION=local
VCS_REF=unknown
```

For real production, publish the bot image with an immutable application tag,
for example:

```env
BOT_IMAGE=ghcr.io/your-org-or-user/tts-hotkey-windows-bot
APP_VERSION=v1.2.3
VCS_REF=<git-sha>
```

The `Release` GitHub Actions workflow publishes semantic version tags such as
`v1.2.3` to GHCR, signs the image, attaches build provenance, and records the
bot image in the GitHub release notes.

Use the same `APP_VERSION` in staging and production only after the staging
promotion gate passes. Keep the previous production `APP_VERSION` in the
release notes so rollback is a config change, not a rebuild.

For Kubernetes GitOps deployments, the equivalent release identity is the
overlay image `newTag` in `deploy/k8s/overlays/staging` or
`deploy/k8s/overlays/prod`. The tag must refer to an immutable GHCR release
image that passed signature, provenance, and critical vulnerability checks.

## Staging Baseline

Staging should mirror the production stack shape:

- Redis
- Postgres
- bot container
- `/health`
- `/ready`
- `/observability`
- restart policy
- the same schema bootstrap files

Staging does not need production capacity, but it must exercise the same
dependency contracts.

## Staging Environment

Create a staging env file from `.env.prod.example`.

Recommended local name:

```text
.env.staging
```

Use separate values from production:

- separate Discord bot token when possible
- separate Postgres database and password
- separate Redis DB or isolated Redis instance
- staging-specific Grafana credentials

Start staging with the same compose file:

```powershell
docker compose --env-file .env.staging -f docker-compose.prod.yml up -d --build
```

For Kubernetes staging, Argo CD reconciles
`deploy/k8s/overlays/staging` through
`deploy/gitops/argocd/staging-application.yaml`. Create runtime secrets outside
the repository before syncing. The public Kustomize overlays reference
`bot-secrets` but do not generate it.

## Staging Promotion Gate

Before production deploy, staging must pass:

```powershell
Invoke-RestMethod http://127.0.0.1:10000/health
Invoke-RestMethod http://127.0.0.1:10000/ready
Invoke-RestMethod http://127.0.0.1:10000/observability
```

After a short bot smoke test produces at least one successful playback sample:

```powershell
.\.venv\Scripts\python.exe scripts/test/quality_gates.py observability --url http://127.0.0.1:10000/observability --config config/quality_gates.json
```

Also confirm:

- Redis and Postgres services are healthy
- bot service is healthy
- the queue drains after the smoke request
- bot logs have no repeated Redis, Postgres, Discord, or engine errors

## Rollback Point

Before deploying production, record:

- current `APP_VERSION` and `VCS_REF`
- target `APP_VERSION` and `VCS_REF`
- env file change summary
- latest Postgres backup path
- rollback owner

Create a pre-release Postgres backup when the release may affect persistence:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/utils/backup_postgres.ps1 `
  -ContainerName tts-bot-postgres `
  -DatabaseName tts_hotkey_windows `
  -DatabaseUser your_postgres_user `
  -BackupDirectory "C:\Backups\tts-bot" `
  -RetentionDays 30
```

## Production Deploy

Deploy the known staging-passed revision:

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml pull bot
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-build
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

If only the bot changed:

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml pull bot
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-deps --no-build bot
```

For Kubernetes production, open a reviewed change that updates
`deploy/k8s/overlays/prod/kustomization.yaml` to the staging-passed image tag.
After merge, sync the Argo CD production application manually. Keep automated
production sync disabled until staging, alerting, and rollback drills are
routine.

## Rollback

Use rollback when the release breaks health, readiness, queue processing,
storage access, or the desktop-connected bot flow.

For Docker image rollback on a runner with access to the production compose
stack, use the `Rollback Bot Image` GitHub Actions workflow. It defaults to a
dry run. For an actual rollback, provide:

- runner labels, for example `["self-hosted","linux","bot-server"]`
- previous `BOT_IMAGE`
- previous `APP_VERSION`
- previous `VCS_REF`
- production env file path
- production compose file path

The workflow pulls the selected image tag, recreates only the bot service, and
validates `/health` and `/ready`.

1. Restore the previous application image tag in `.env.prod`.

```env
APP_VERSION=<previous-known-good-version>
VCS_REF=<previous-known-good-sha>
```

2. Restore the previous env file if the incident is configuration-related.

3. Pull and restart the bot without rebuilding.

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml pull bot
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-deps --no-build bot
```

4. Validate recovery.

```powershell
Invoke-RestMethod http://127.0.0.1:10000/health
Invoke-RestMethod http://127.0.0.1:10000/ready
Invoke-RestMethod http://127.0.0.1:10000/observability
```

5. If persistence was changed and code rollback is insufficient, follow
   [BACKUP_AND_RESTORE_DATABASE.md](BACKUP_AND_RESTORE_DATABASE.md) with the
   selected backup.

For Kubernetes GitOps rollback, revert the Git commit that promoted the bad
`newTag`, or commit the previous known-good tag to the affected overlay and
sync the Argo CD application. Do not patch the live Deployment directly except
as a short emergency containment step; if that happens, restore Git as the
source of truth immediately after recovery.

## Done Criteria

A deploy or rollback is done only when:

- `/health` returns healthy
- `/ready` returns ready
- the bot service health is `healthy` in Docker
- a short TTS smoke request completes
- the live observability SLI gate passes after smoke traffic
- Prometheus alerts route through Alertmanager and reach the incident channel
  during staging validation when alert routing changed
- any validation gap is recorded in the release notes
