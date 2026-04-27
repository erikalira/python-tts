# Documentation

This directory contains the repository's supporting documentation. The root
`README.md` stays short on purpose, while the details live here.

## Getting Started

- [getting-started/SETUP.md](getting-started/SETUP.md): virtual environment setup, installation, and activation on Windows and Linux
- [getting-started/TESTING.md](getting-started/TESTING.md): automated test structure and local execution

## Understand The System

- [architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md): architecture overview and layer map
- [desktop/DESKTOP_APP_GUIDE.md](desktop/DESKTOP_APP_GUIDE.md): desktop app guide
- [architecture/RUNTIME_FLOWS.md](architecture/RUNTIME_FLOWS.md): bot and Desktop App entrypoints, composition roots, and main runtime flows
- [architecture/BOT_DESKTOP_HTTP_CONTRACT.md](architecture/BOT_DESKTOP_HTTP_CONTRACT.md): explicit HTTP wire contract between the Desktop App and the bot runtime
- [architecture/SHARED_VS_RUNTIME_DECISION.md](architecture/SHARED_VS_RUNTIME_DECISION.md): practical guide for deciding whether code belongs in shared layers or a specific runtime
- [architecture/EXPLICIT_CONTRACTS_GUIDE.md](architecture/EXPLICIT_CONTRACTS_GUIDE.md): practical guide for deciding when a boundary needs a DTO, Protocol, or other explicit contract
- [architecture/ARCHITECTURE_DIAGRAMS.md](architecture/ARCHITECTURE_DIAGRAMS.md): curated architecture diagrams grouped by layer and runtime
- [architecture/ARCHITECTURE_DIAGRAMS_GENERATED.md](architecture/ARCHITECTURE_DIAGRAMS_GENERATED.md): entrypoint for the automatic diagram set generated from code
- [architecture/ARCHITECTURE_TRANSITIONS.md](architecture/ARCHITECTURE_TRANSITIONS.md): repository-specific examples for temporary facades, compatibility paths, and transition structure
- [reference/ENGINEERING_REFERENCES.md](reference/ENGINEERING_REFERENCES.md): books and engineering concepts that inform repository design decisions
- [adr/README.md](adr/README.md): architecture decision records for durable technical choices and tradeoffs

## Operate And Deploy

- [deploy/DEPLOYMENT_GUIDE.md](deploy/DEPLOYMENT_GUIDE.md): entrypoint for choosing the right server deployment guide
- [operations/BASELINE_AND_RELEASE_GATES.md](operations/BASELINE_AND_RELEASE_GATES.md): Phase 0 baseline, initial SLI/SLO definitions, and release gates for bot and desktop
- [operations/ELITE_UPGRADE_PLAN.md](operations/ELITE_UPGRADE_PLAN.md): phased plan for supply chain security, release engineering, IaC, advanced tests, runtime security, and packaging upgrades
- [operations/SECURITY_GATES.md](operations/SECURITY_GATES.md): dependency scanning, CodeQL, dependency review, and bot rate-limit release expectations
- [operations/PRODUCTION_RUNBOOKS.md](operations/PRODUCTION_RUNBOOKS.md): incident runbooks for lock starvation, stuck queues, and TTS engine degradation
- [operations/DR_DRILLS.md](operations/DR_DRILLS.md): production recovery drills for Postgres restore, Redis recovery, and version rollback
- [operations/RELEASE_CHECKLIST.md](operations/RELEASE_CHECKLIST.md): release checklist covering bot, desktop, deploy, and post-deploy metrics
- [deploy/ENVIRONMENTS.md](deploy/ENVIRONMENTS.md): local and production environment variables for bot and Desktop App
- [deploy/WINDOWS_BOT_DEPLOY.md](deploy/WINDOWS_BOT_DEPLOY.md): WinSW deployment guide for keeping the Discord bot running as a Windows service
- [deploy/BOT_PRODUCTION_PERSISTENCE.md](deploy/BOT_PRODUCTION_PERSISTENCE.md): recommended persistence architecture for production bot deploys
- [deploy/DOCKER_POSTGRES_DEPLOY.md](deploy/DOCKER_POSTGRES_DEPLOY.md): run the Discord bot with Docker and Postgres
- [../docker-compose.postgres.yml](../docker-compose.postgres.yml): local Postgres-only compose file for testing `CONFIG_STORAGE_BACKEND=postgres`
- [deploy/BACKUP_AND_RESTORE_DATABASE.md](deploy/BACKUP_AND_RESTORE_DATABASE.md): backup and restore flow for the Dockerized Postgres database
- [deploy/STAGING_AND_ROLLBACK.md](deploy/STAGING_AND_ROLLBACK.md): staging promotion and rollback flow for the Docker production stack
- [desktop/WINDOWS_BUILD_GUIDE.md](desktop/WINDOWS_BUILD_GUIDE.md): Windows executable build flow

## Maintenance

- [maintenance/DEPENDENCY_MAINTENANCE.md](maintenance/DEPENDENCY_MAINTENANCE.md): dependency upgrade workflow, tooling, and validation checklist

## Governance

- [../.specify/README.md](../.specify/README.md): canonical Spec Kit governance and workflow index
- [../.specify/memory/constitution.md](../.specify/memory/constitution.md): repository constitution and non-negotiable rules
- [../.specify/memory/ai-pitfalls.md](../.specify/memory/ai-pitfalls.md): common AI-assisted change pitfalls to avoid
- [../.specify/sync-report-template.md](../.specify/sync-report-template.md): template for constitution sync reports
- [../.specify/templates/spec-template.md](../.specify/templates/spec-template.md): feature specification standard
- [../.specify/templates/plan-template.md](../.specify/templates/plan-template.md): implementation plan standard
- [../.specify/templates/tasks-template.md](../.specify/templates/tasks-template.md): task breakdown standard
- [../.specify/review-checklist.md](../.specify/review-checklist.md): canonical review and self-review checklist
- [../.specify/transition-cleanup.md](../.specify/transition-cleanup.md): canonical temporary compatibility cleanup rule
- [../.specify/change-map.md](../.specify/change-map.md): canonical guide for where to start a change
- [../AGENTS.md](../AGENTS.md): derivative agent summary for the current repository
- [../.github/copilot-instructions.md](../.github/copilot-instructions.md): derivative GitHub Copilot summary aligned to `.specify/`

## Conventions

- `docs/` contains durable architecture and operational guides
- `docs/operations/` contains operational baselines and release criteria
- `docs/operations/` also contains production runbooks, DR drills, and release checklists
- `docs/architecture/diagrams/` contains editable Mermaid architecture sources
- `docs/adr/` contains architecture decision records for major technical choices
- `.specify/` contains canonical project guidance and feature workflow templates
- AI/tool-specific instruction files should remain derivative of `.specify/`
- `.agents/` and `.codex/` contain project-specific agent skills and playbooks
  that remain derivative of `.specify/` for repository policy

## Navigation

- [Back to root README](../README.md)
