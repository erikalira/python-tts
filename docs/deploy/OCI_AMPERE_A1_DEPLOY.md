# OCI Ampere A1 Deploy

Run the Discord bot continuously on a small ARM64 Oracle Cloud instance.

This is the recommended lightweight always-on cloud deployment for the bot when
an ARM64 OCI Ampere A1 instance is available. It is an additional target: the
Windows, Docker/Postgres, and Render shapes remain fully supported. See
[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) to compare them.

The decision behind this target is recorded in
[ADR 0008](../adr/0008-oci-ampere-a1-deployment-target.md).

## Architecture

```mermaid
flowchart TD
    dev[Developer] -->|git push tag vX.Y.Z| gh[GitHub]
    gh --> actions[GitHub Actions Release]
    actions -->|buildx amd64 + arm64| ghcr[("GHCR multi-arch manifest<br/>signed, SBOM, provenance")]

    ghcr -->|existing target| beelink[Beelink / Docker Compose<br/>linux/amd64]
    ghcr -->|docker pull vX.Y.Z| vm

    subgraph oci["Oracle Cloud Infrastructure"]
        subgraph vcn["VCN 10.20.0.0/16"]
            nsg["Network Security Group<br/>22 from admin CIDR<br/>80/443 only when HTTPS enabled"]
            subgraph vm["VM.Standard.A1.Flex — 1 OCPU / 6 GB — Ubuntu 24.04 ARM64"]
                caddy["Caddy :443<br/>automatic TLS"]
                bot["python-tts container<br/>127.0.0.1:10000"]
                cfg[("/opt/python-tts/configs<br/>bind mount")]
                caddy --> bot
                bot --- cfg
            end
        end
    end

    bot -->|outbound WSS| discord[Discord Gateway and Voice]
    desktop[Desktop App] -->|"HTTPS POST /speak<br/>X-Bot-Token"| caddy

    deployflow[GitHub Actions Deploy OCI<br/>workflow_dispatch] -->|SSH, pinned host key| vm

    style ghcr fill:#1f6feb,color:#fff
    style bot fill:#238636,color:#fff
    style cfg fill:#8957e5,color:#fff
```

What is deliberately **not** on this host: Postgres, Redis, Grafana, Prometheus,
Tempo, Alertmanager, and the OTel collector. The bot uses JSON config storage
and an in-memory queue so it fits comfortably in 1 OCPU and 6 GB.

## Prerequisites

| Requirement | Notes |
| --- | --- |
| OCI account | With a compartment you can create resources in |
| OCI API credentials | For OpenTofu. Configure with `oci setup config` or the `OCI_CLI_*` environment variables |
| OpenTofu | `>= 1.6.0` |
| SSH key pair | Public key goes to OpenTofu; the private key never does |
| Discord bot token | From the Discord Developer Portal |
| `BOT_SPEAK_TOKEN` | Generate with `openssl rand -hex 32` |
| Domain name | Optional. Required only for public HTTPS `/speak` |

### Free-tier notes

Read this before applying.

Oracle's Always Free allocation is a property of **your tenancy**, not of this
repository, and Oracle's published limits and terms can change. Ampere A1
capacity is **tenancy-wide**: other instances in the same tenancy consume the
same allocation.

Verify your current Always Free allocation in the OCI console before running
`tofu apply`. This configuration:

- defaults to 1 OCPU and 6 GB, and rejects more than 4 OCPUs or 24 GB
- defaults to a 50 GB boot volume, and rejects more than 200 GB
- provisions no load balancer, database, or other managed service
- creates nothing that bills silently

These are guardrails against an accidentally large instance. They are not a
guarantee that your tenancy will not be charged. Confirm your own limits.

## Provisioning

```bash
cd infra/environments/oci

cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your OCIDs, region, availability domain,
# SSH public key, and administrative CIDR.

tofu init
tofu fmt -check
tofu validate
tofu plan
tofu apply
```

`terraform.tfvars` is gitignored. Never commit it.

Record the outputs:

```bash
tofu output instance_public_ip
tofu output ssh_command
```

### Required variables

| Variable | Default | Notes |
| --- | --- | --- |
| `tenancy_ocid` | — | Required |
| `compartment_ocid` | — | Required |
| `region` | — | For example `sa-saopaulo-1` |
| `availability_domain` | — | For example `Uocm:SA-SAOPAULO-1-AD-1` |
| `ssh_public_key` | — | Public key material only |
| `ssh_allowed_cidrs` | — | Required. `0.0.0.0/0` is rejected |
| `instance_ocpus` | `1` | Max 4 |
| `instance_memory_gb` | `6` | Max 24 |
| `boot_volume_size_gb` | `50` | Max 200 |
| `instance_image_ocid` | `""` | Empty discovers the newest Ubuntu 24.04 ARM64 image |
| `enable_public_https` | `false` | Opens 80 and 443 |
| `public_hostname` | `""` | Required when HTTPS is enabled |
| `bot_http_allowed_cidrs` | `[]` | Opt-in direct access. `0.0.0.0/0` is rejected |

### Image discovery

The module resolves the newest `Canonical Ubuntu 24.04` ARM64 platform image
through the `oci_core_images` data source, filtered by shape. If your tenancy or
region does not return a match, `tofu plan` fails with a clear message; set
`instance_image_ocid` explicitly to the OCID from the OCI console
(**Compute → Instances → Create → Change image**).

A platform image update alone will not recreate a running instance: the
instance ignores changes to the discovered image ID. To move to a newer image,
recreate the instance deliberately.

## First deployment

Cloud-init installs Docker and prepares `/opt/python-tts`. Wait for it to
finish, then confirm:

```bash
ssh ubuntu@<PUBLIC_IP> 'cloud-init status --wait && docker compose version'
```

Create the runtime configuration locally from the example:

```bash
cp .env.oci.example .env.oci
# Fill in DISCORD_TOKEN, BOT_SPEAK_TOKEN, and BOT_IMAGE.
# Set PUBLIC_HOSTNAME only if you enabled HTTPS.
```

Add the host to `known_hosts` before uploading anything sensitive:

```bash
ssh-keyscan -H <PUBLIC_IP> >> ~/.ssh/known_hosts
```

Install the configuration and deployment assets:

```bash
./scripts/deploy/oci-bootstrap-env.sh --host <PUBLIC_IP> --env-file ./.env.oci
```

The script uploads `.env.oci` over SSH, installs it as
`/opt/python-tts/.env.runtime` with mode `0600`, and copies the compose file,
Caddyfile, and deploy script. It refuses to run if `DISCORD_TOKEN` or
`BOT_SPEAK_TOKEN` is empty or still a placeholder.

`.env.oci` is gitignored, but it holds real secrets. Store it in a password
manager and delete the local copy when you are done.

Deploy a released version:

```bash
ssh ubuntu@<PUBLIC_IP> '/opt/python-tts/scripts/oci-deploy.sh v1.2.3'
```

## DNS and HTTPS

Public `/speak` access is off by default. To enable it:

1. Set the variables and re-apply:

   ```hcl
   enable_public_https = true
   public_hostname     = "tts.example.com"
   ```

   ```bash
   tofu apply
   ```

   This opens `80/tcp` and `443/tcp`. Port 80 exists only for the ACME
   HTTP-01 challenge and the redirect to HTTPS.

2. Create one DNS record:

   ```text
   tts.example.com.  A  <OCI_PUBLIC_IP>
   ```

3. Set `PUBLIC_HOSTNAME` in `.env.oci`, re-run the bootstrap script, and
   redeploy. The deploy script starts the `https` profile automatically when
   `PUBLIC_HOSTNAME` is set.

Caddy requests a Let's Encrypt certificate on first start and renews it
automatically. Certificates persist in `/opt/python-tts/caddy/data`.

The Desktop App then points at:

```text
DISCORD_BOT_URL=https://tts.example.com
```

`BOT_SPEAK_TOKEN` still guards `/speak`, sent as the `X-Bot-Token` header. Caddy
adds transport security; it does not replace the token.

Only `/speak`, `/voice-context`, and `/health` are proxied. `/ready`,
`/observability`, `/version`, and `/about` are reachable from the host only —
they describe runtime internals and have no authentication of their own.

### Without a hostname

If you do not configure HTTPS, the bot port is not reachable from the internet.
Use an SSH tunnel for administration and testing:

```bash
ssh -L 10000:127.0.0.1:10000 ubuntu@<PUBLIC_IP>
# then, locally:
curl http://127.0.0.1:10000/health
```

A CIDR allowlist for direct access exists as an explicit opt-in
(`bot_http_allowed_cidrs`), but it carries plain HTTP and is not recommended.

## GitHub Actions

Create a `oci-production` environment in the repository, then add:

| Secret | Value |
| --- | --- |
| `OCI_DEPLOY_HOST` | Instance public IP or hostname |
| `OCI_DEPLOY_USER` | `ubuntu` |
| `OCI_DEPLOY_SSH_KEY` | Private key authorized on the instance |
| `OCI_DEPLOY_KNOWN_HOSTS` | Output of `ssh-keyscan -H <PUBLIC_IP>` |

Optional repository variable:

| Variable | Default |
| --- | --- |
| `OCI_APP_DIR` | `/opt/python-tts` |

`OCI_DEPLOY_KNOWN_HOSTS` pins the host key. Host key verification is never
disabled; a substituted host cannot receive a deployment. No application secret
is transmitted by the workflow — `DISCORD_TOKEN` and `BOT_SPEAK_TOKEN` live on
the instance.

## Deployment

Releasing and deploying are separate operations.

**Release** publishes the artifact:

```bash
git tag v1.2.3
git push origin v1.2.3
```

The `Release` workflow builds `linux/amd64` and `linux/arm64`, verifies the
published manifest contains both, scans, signs, and attests it.

**Deploy** promotes an existing release:

```text
Actions -> Deploy OCI -> Run workflow
  release_tag = v1.2.3
  dry_run     = false
```

The workflow validates the tag format, confirms the GHCR manifest contains
`linux/arm64`, connects over SSH with a pinned host key, runs the remote deploy
script, and reports the health response. Use `dry_run = true` to validate a tag
without touching the host.

Equivalently, from the instance:

```bash
ssh ubuntu@<PUBLIC_IP> '/opt/python-tts/scripts/oci-deploy.sh v1.2.3'
```

The deploy script:

1. validates the tag is semantic, rejecting `latest`
2. confirms the image exists and has a `linux/arm64` manifest entry
3. pulls the image
4. records the current version as `PREVIOUS_APP_VERSION`
5. restarts the container on the new tag
6. waits for `/health`, then `/ready`
7. fails with container logs if either check does not pass
8. prunes dangling layers only, keeping tagged images for fast rollback

Pushes never deploy automatically.

## Rollback

Rollback redeploys a known-good tag. It never rebuilds an image.

```text
current:  v1.3.0
previous: v1.2.4

deploy v1.3.0  ->  health/readiness fail  ->  rollback to v1.2.4
```

**On the instance**, using the recorded previous version:

```bash
ssh ubuntu@<PUBLIC_IP> '/opt/python-tts/scripts/oci-deploy.sh --rollback'
```

**Explicitly**, to any known-good tag:

```bash
ssh ubuntu@<PUBLIC_IP> '/opt/python-tts/scripts/oci-deploy.sh v1.2.4'
```

**Through GitHub Actions**, which is the same operation:

```text
Actions -> Deploy OCI -> Run workflow
  release_tag = v1.2.4
```

The repository's `Rollback Bot Image` workflow also targets this host, since its
inputs are deployment-shape agnostic. Use these inputs:

```text
runner       = ["ubuntu-latest"]   # only if the runner can reach the host
bot_image    = ghcr.io/erikalira/tts-hotkey-windows-bot
app_version  = v1.2.4
env_file     = /opt/python-tts/.env.runtime
compose_file = /opt/python-tts/compose.yaml
health_url   = http://127.0.0.1:10000/health
ready_url    = http://127.0.0.1:10000/ready
```

That workflow expects to run **on** the target host, so it needs a self-hosted
runner there. For this single-node target, `Deploy OCI` with an earlier tag is
the simpler path and is the documented default.

Because the previous image is not pruned, rollback does not re-download it.

## Logs

```bash
ssh ubuntu@<PUBLIC_IP>
cd /opt/python-tts

docker compose --env-file .env.runtime -f compose.yaml logs -f bot
docker compose --env-file .env.runtime -f compose.yaml logs --tail 100 bot
docker compose --env-file .env.runtime -f compose.yaml ps
```

Caddy logs, when the HTTPS profile is running:

```bash
docker compose --env-file .env.runtime -f compose.yaml --profile https logs caddy
```

Log rotation is configured in two places so an always-on bot cannot fill the
disk: the Docker daemon caps every container at 3 files of 10 MB, and the
compose services set the same limits explicitly.

## Health

From the instance:

```bash
curl http://127.0.0.1:10000/health   # {"status": "healthy"}
curl http://127.0.0.1:10000/ready    # {"status": "ready", "dependencies": [...]}
```

`/ready` returns `503` until dependencies are satisfied, which is what the
deploy script waits on.

Through an SSH tunnel, or over HTTPS when enabled:

```bash
curl https://tts.example.com/health
```

Confirm the Discord side by checking that the bot appears online in your server
and responds to a command.

## Reboot recovery

The bot returns automatically after a reboot, a Docker restart, or a crash:

- the container uses `restart: unless-stopped`
- Docker is enabled at boot by cloud-init (`systemctl enable --now docker`)
- the Docker daemon runs with `live-restore`

Verify deliberately:

```bash
ssh ubuntu@<PUBLIC_IP> 'sudo reboot'
# wait about a minute
ssh ubuntu@<PUBLIC_IP> 'docker ps --format "{{.Names}}\t{{.Status}}"'
ssh ubuntu@<PUBLIC_IP> 'curl -s http://127.0.0.1:10000/health'
```

Both the container and the health endpoint should come back without manual
intervention. Confirm Docker is enabled at boot:

```bash
ssh ubuntu@<PUBLIC_IP> 'systemctl is-enabled docker'
```

## Disaster recovery

This host holds very little state, which is the point.

| What | Where | Backup |
| --- | --- | --- |
| Runtime secrets | `/opt/python-tts/.env.runtime` | Password manager or secret store. **Never** a public backup |
| Bot configuration | `/opt/python-tts/configs/` | Regular copy; this is the only stateful data |
| Deployed version | `APP_VERSION` in `.env.runtime` | Also in the GitHub release history |
| Certificates | `/opt/python-tts/caddy/data` | Not required; Caddy re-issues them |

Back up the configuration directory:

```bash
ssh ubuntu@<PUBLIC_IP> 'sudo tar czf - -C /opt/python-tts configs' > tts-configs-backup.tar.gz
```

Full recovery on a new instance:

```bash
tofu apply                                    # provision
./scripts/deploy/oci-bootstrap-env.sh ...     # reinstall secrets
scp tts-configs-backup.tar.gz ubuntu@<NEW_IP>:/tmp/
ssh ubuntu@<NEW_IP> 'sudo tar xzf /tmp/tts-configs-backup.tar.gz -C /opt/python-tts && sudo chown -R 1000:1000 /opt/python-tts/configs'
ssh ubuntu@<NEW_IP> '/opt/python-tts/scripts/oci-deploy.sh v1.2.3'
```

There is no database to restore on this target. If you need durable Postgres
persistence, use [DOCKER_POSTGRES_DEPLOY.md](DOCKER_POSTGRES_DEPLOY.md) instead
and see [BACKUP_AND_RESTORE_DATABASE.md](BACKUP_AND_RESTORE_DATABASE.md).

## Destroy

```bash
cd infra/environments/oci
tofu destroy
```

This permanently deletes:

- the instance and its **boot volume**, including `/opt/python-tts/configs`
  (all bot guild configuration) and `/opt/python-tts/.env.runtime`
- the VCN, subnet, internet gateway, route table, and network security group
- the instance's public IP — a new instance gets a new address, so the DNS
  record must be updated

Back up `configs/` and confirm you still hold `DISCORD_TOKEN` and
`BOT_SPEAK_TOKEN` before destroying. Published GHCR images are not affected.

## Related documents

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — choose a deployment shape
- [ENVIRONMENTS.md](ENVIRONMENTS.md) — environment variable reference
- [STAGING_AND_ROLLBACK.md](STAGING_AND_ROLLBACK.md) — release promotion and rollback concepts
- [ADR 0008](../adr/0008-oci-ampere-a1-deployment-target.md) — why this target exists
- [../security/THREAT_MODEL.md](../security/THREAT_MODEL.md) — runtime threat model
