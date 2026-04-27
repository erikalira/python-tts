# Runtime Threat Model

This document covers the runtime security model for the Discord bot HTTP
surface, especially the Desktop App to bot `/speak` flow.

## Scope

In scope:

- Discord bot HTTP endpoints exposed by `src/infrastructure/http/server.py`
- Desktop App calls to bot endpoints through `src/desktop/services/discord_bot_client.py`
- Discord bot token, desktop-to-bot shared secrets, Redis queue data, Postgres
  configuration data, and runtime logs
- local development, Docker Compose production, and future Kubernetes
  deployment shapes

Out of scope:

- Discord platform authentication and gateway transport security
- host operating system hardening outside the deployment runbooks
- user identity management beyond the single Desktop App to bot integration
  contract

## Assets

| Asset | Why it matters | Primary controls |
| --- | --- | --- |
| `DISCORD_TOKEN` | Grants control of the bot account. | Secret manager or restricted `.env`, never logged, never committed. |
| `/speak` endpoint | Can enqueue audio into Discord voice channels. | bind address, shared token, rate limit, payload limits, CORS allowlist. |
| Redis queue | Carries queued speech items and processing leases. | private network, credentials when exposed, key prefix, TTLs. |
| Postgres config | Stores durable bot configuration preferences. | private network, credentials, backup and restore controls. |
| Desktop config | Stores bot URL and caller identity preferences. | local user profile permissions, no privileged secrets by default. |
| Logs and telemetry | Help operations but may reveal identifiers or abuse patterns. | avoid request bodies and secrets, keep structured result codes. |

## Trust Boundaries

The Desktop App and bot are independent applications. Their HTTP boundary is a
wire contract, not an internal function call.

Default trusted boundary:

- local development: bot binds to `127.0.0.1`, Desktop App calls
  `http://localhost:10000`

Expanded boundary:

- Docker Compose or cloud: bot may bind to `0.0.0.0`
- any non-local bind must treat `/speak` as exposed until network policy,
  authentication, CORS, and payload limits are confirmed

External systems:

- Discord gateway and voice services are outside repository control
- Redis, Postgres, OTLP collectors, and container registries must be reachable
  only from trusted networks or authenticated clients

## Actors

| Actor | Expected behavior | Security concern |
| --- | --- | --- |
| Desktop App user | sends short speech requests to their configured bot | accidental misconfiguration or stale bot URL |
| Bot operator | manages env vars, releases, rollbacks, logs | secret leakage or unsafe production defaults |
| Same-host process | can call localhost endpoints | unauthorized `/speak` submissions |
| Network attacker | may reach public bot HTTP port if exposed | spam, queue exhaustion, probing, token brute force |
| Dependency attacker | compromises package or image supply chain | runtime compromise through install or image build |

## Abuse Cases

1. Unauthenticated caller sends repeated `/speak` requests and fills the queue.
2. Caller submits very large JSON bodies to waste memory or CPU.
3. Browser context submits `/speak` through an overly broad CORS policy.
4. Caller forges `guild_id`, `channel_id`, or `member_id` values to target
   unexpected voice contexts.
5. Operator exposes `DISCORD_BOT_HOST=0.0.0.0` without a shared token.
6. Logs capture secrets, request bodies, or full connection strings.
7. Redis or Postgres becomes reachable from untrusted networks.
8. A bad release image is deployed and must be rolled back to a known-good tag.

## Runtime Controls

Required controls for `/speak` before treating it as internet or LAN exposed:

- explicit CORS allowlist, defaulting to no browser origins
- shared token authentication for `/speak`
- rate limit by authenticated token when present, then by caller/source scope
- maximum request body size
- maximum speech text length
- strict JSON object shape and `application/json` content type
- typed error responses for auth, validation, rate-limit, queue, and health
  failures

Operational controls:

- keep `DISCORD_TOKEN`, database passwords, Redis passwords, and `/speak`
  shared tokens in environment variables or a secret manager
- never commit `.env`, production env files, generated SBOMs containing local
  paths, or scanner reports with sensitive host details
- prefer private network access for Redis, Postgres, and OTLP collectors
- use immutable GHCR image tags and the rollback workflow for bad releases

## Logging Rules

Logs may include:

- endpoint name, result code, status code, guild/member identifiers when needed
  for operations, rate-limit scope, and retry-after seconds

Logs must not include:

- `DISCORD_TOKEN`
- shared `/speak` token
- request authorization headers
- full `/speak` text payloads
- full database or Redis connection strings with passwords

## Open Follow-Ups

- Add contract tests for `/speak` success, auth failure, validation failure,
  rate-limit failure, queue failure, and health endpoints.
- Add automated dependency-failure tests for Redis and Postgres unavailability.
- Decide whether future multi-user exposure needs per-user tokens or signed
  requests instead of a single shared integration token.
