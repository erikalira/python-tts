# Distributed TTS System

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7ed90fe1cc6f4090a7386df4681df463)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/7ed90fe1cc6f4090a7386df4681df463)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

Production-grade **Text-to-Speech system** with queue orchestration,
infrastructure as code, and an operational lifecycle that covers deploy,
observability, validation, and rollback.

This repository contains two independent applications:

- A Discord bot that joins voice channels and plays TTS audio
- A Windows Desktop App that captures text with hotkeys and sends it to the bot

The project follows Clean Architecture and keeps shared behavior in the
application/core layers so the Discord bot and Desktop App can evolve
independently without duplicating business logic.

## Contents

- [Overview](#overview)
- [Why This Project Matters](#why-this-project-matters)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Operational Capabilities](#operational-capabilities)
- [Quick Start](#quick-start)
- [Testing](#testing)
- [Documentation](#documentation)
- [Future Improvements](#future-improvements)

## Overview

This project is a distributed TTS system designed with real production concerns
in mind:

- Queue-based audio processing
- Desktop-to-bot communication through an explicit HTTP contract
- Infrastructure as Code with OpenTofu
- CI/CD with release and rollback workflows
- Health, readiness, telemetry, and runtime observability
- Resilience validation through load and chaos testing

## Why This Project Matters

The goal is to demonstrate backend, platform, and desktop integration skills in
one coherent system. The repository emphasizes system design, explicit
contracts, operational readiness, and maintainable boundaries over isolated
feature work.

## Architecture

The repository is organized around Clean Architecture boundaries:

- `src/core/`: domain concepts and shared core behavior
- `src/application/`: use cases and inward-facing contracts
- `src/infrastructure/`: concrete adapters for external systems
- `src/presentation/`: Discord and HTTP presentation entrypoints
- `src/desktop/`: Windows Desktop App runtime

Key runtime components:

- **Bot Runtime**: HTTP API (`/speak`, `/health`, `/ready`) and Discord voice flow
- **Desktop App**: hotkey-driven text capture and bot request dispatch
- **Queue Layer**: in-memory and Redis-backed queue implementations
- **Persistence**: JSON storage for local development and Postgres for production-style flows

## Tech Stack

Backend and runtime:

- Python
- aiohttp
- Redis
- PostgreSQL

Infrastructure and delivery:

- Docker and Docker Compose
- Kubernetes with Kustomize
- OpenTofu
- GitHub Actions
- GHCR image publishing

Observability and validation:

- OpenTelemetry
- Prometheus
- Grafana
- pytest
- Load and chaos testing workflows

## Operational Capabilities

- Token-based authentication for `/speak`
- Rate limiting by token and user scope
- Payload size limits and CORS allowlist
- `/health` liveness endpoint
- `/ready` dependency readiness endpoint
- `/observability` runtime snapshot endpoint
- Semantic version release workflow
- Manual rollback workflow with health validation
- Multi-environment infrastructure contracts for dev, staging, and production

## Quick Start

For the full setup flow, including virtual environment creation, dependency
sync, FFmpeg, Redis, and Postgres options, see
[docs/getting-started/SETUP.md](docs/getting-started/SETUP.md).

Minimal local flow:

```bash
uv sync --locked
```

Create a `.env` file with at least:

```env
DISCORD_TOKEN=your_token_here
DISCORD_BOT_URL=http://127.0.0.1:10000
DISCORD_BOT_PORT=10000
```

Start the bot:

```bash
python -m src.bot
```

In another terminal, run the Desktop App:

```bash
python app.py
```

## Testing

```bash
uv run pytest
```

Test structure and local execution details live in
[docs/getting-started/TESTING.md](docs/getting-started/TESTING.md).

## Windows Executable Build

On Windows, use the official script:

```powershell
./scripts/build/build_clean_architecture.ps1
```

On Linux, build the `.exe` through the CI workflow that runs in a Windows
environment.

## Documentation

Use the root README as the portfolio and project entrypoint. Detailed setup,
architecture, deployment, security, operations, and governance documentation
lives in the dedicated docs:

- [Documentation index](docs/README.md)
- [Environment setup guide](docs/getting-started/SETUP.md)
- [Testing guide](docs/getting-started/TESTING.md)
- [Project architecture](docs/architecture/ARCHITECTURE.md)
- [Desktop App guide](docs/desktop/DESKTOP_APP_GUIDE.md)
- [Server deployment guide](docs/deploy/DEPLOYMENT_GUIDE.md)
- [Threat model](docs/security/THREAT_MODEL.md)
- [Canonical constitution and workflow](.specify/README.md)

## Future Improvements

- Cloud provisioning for GCP or AWS through OpenTofu
- Horizontal scaling with HPA
- Advanced SLOs and alerting
- Multi-tenant support and billing boundaries

## License

Copyright (c) 2026 Erika Lira. All rights reserved.

This repository is public for portfolio review and technical evaluation only.
No permission is granted to copy, modify, distribute, sublicense, publish, sell,
host, deploy, or use this software commercially without explicit prior written
permission. See [LICENSE](LICENSE).

## Author

Erika Lira

## Notes

This project is not just a TTS tool. It is an engineering-focused system built
to explore production-grade backend, desktop, and platform patterns.
