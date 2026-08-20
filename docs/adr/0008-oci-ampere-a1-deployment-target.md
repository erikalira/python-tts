# ADR 0008: Add OCI Ampere A1 As A Lightweight Always-On Deployment Target

## Status

Accepted

## Context

The Discord bot needs to run continuously. The existing deployment shapes each
carry a cost that does not fit an always-on hobby-scale bot:

- The Windows/WinSW shape needs a machine that stays powered on.
- The Docker/Postgres production stack runs Postgres, Redis, Grafana,
  Prometheus, Tempo, Alertmanager, and the OTel collector. That is the right
  shape for a production-like environment, and the wrong shape for a small
  single-node cloud VM.
- Render and similar platforms sleep or bill by uptime.

An OCI Ampere A1 instance can host the bot continuously at very low cost, but it
is ARM64, and the release pipeline previously published an `amd64`-only image.

ADR 0006 established OpenTofu as the infrastructure baseline and required a
recorded decision before adding the first provider-specific module. This ADR is
that decision.

## Decision

Add OCI Ampere A1 as an additional deployment target, alongside the existing
shapes rather than replacing any of them.

Four choices define the target:

1. **The released image becomes multi-architecture.** The existing Buildx step
   in the release workflow publishes `linux/amd64` and `linux/arm64` under one
   manifest. The same source produces both platforms; no Oracle-specific
   application build exists. The release fails if the published manifest is
   missing a platform.

2. **The OCI runtime is deliberately lightweight.** `CONFIG_STORAGE_BACKEND=json`
   with a bind-mounted config directory, `TTS_QUEUE_BACKEND=inmemory`, and
   `OTEL_ENABLED=false`. Postgres, Redis, and the observability stack are not
   deployed on this host. `/health` and `/ready` remain the validation surface.
   This trades durable config storage and queue coordination for fitting in
   1 OCPU and 6 GB, which is the point of the target.

3. **Infrastructure and application secrets stay separate.** OpenTofu owns the
   VCN, subnet, gateway, route table, network security group, and instance.
   `DISCORD_TOKEN` and `BOT_SPEAK_TOKEN` are installed on the instance over SSH
   by a bootstrap script and never enter variables, cloud-init user data, or
   state. Instance metadata is readable from the instance and is stored in
   state, so it carries no secret.

4. **The bot HTTP port is never published to the internet.** The container port
   binds to loopback on the host. Public `/speak` access is an opt-in Caddy
   reverse proxy on 443 with automatic TLS, gated by the unchanged
   `BOT_SPEAK_TOKEN`. Without a hostname, an SSH tunnel is the documented
   administrative path.

Release and deployment stay separate operations. Tagging publishes an artifact;
a manually dispatched workflow deploys an already released tag to OCI.

## Consequences

- `infra/environments/oci` is the first environment with real provider
  resources. The other environments keep the contract-only shape.
- The release workflow now builds under QEMU emulation for ARM64, so releases
  take longer. The `container-image` job in the test workflow surfaces ARM64
  build failures before a tag is cut.
- The bot's JSON config on this host lives in a single directory on one boot
  volume. Recovery means restoring that directory and redeploying a tag; there
  is no database to restore. This is recorded in the deployment guide's
  disaster recovery section.
- Free-tier eligibility is a property of the tenancy, not of this repository.
  Variable validation caps the instance at a small size and rejects
  `0.0.0.0/0` on SSH, but the operator must verify their own Always Free
  allocation before applying.
- Adding a second provider module later should follow this same split:
  infrastructure in OpenTofu, application secrets installed out of band.

## Alternatives Considered

- **Deploy the full production compose stack on the A1 instance.** Rejected:
  Postgres, Redis, and four observability services do not leave useful headroom
  on 1 OCPU / 6 GB, and the bot is the only thing that must stay up.
- **Publish a separate `-arm64` image tag.** Rejected: it splits the supply
  chain, and signing, provenance, and scanning would have to be duplicated per
  tag. A single multi-platform manifest keeps one signed digest per release.
- **Expose port 10000 with a CIDR allowlist as the default.** Rejected as a
  default because home IP addresses change and the endpoint would then carry
  plain HTTP. It remains available as an explicit opt-in variable.
- **Kubernetes (k3s) on the instance.** Rejected: a single-node cluster adds a
  control plane's overhead to a host chosen for having very little to spare.
