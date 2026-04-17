# Documentation

This directory contains the repository's supporting documentation. The root
`README.md` stays short on purpose, while the details live here.

## Main guides

- [SETUP.md](SETUP.md): ambiente virtual, instalacao e ativacao no Windows e Linux
- [TESTING.md](TESTING.md): automated test structure and local execution
- [ENVIRONMENTS.md](ENVIRONMENTS.md): local and production environment variables for bot and Desktop App
- [WINDOWS_BOT_SERVICE.md](WINDOWS_BOT_SERVICE.md): WinSW deployment guide for keeping the Discord bot running as a Windows service
- [BOT_PRODUCTION_PERSISTENCE.md](BOT_PRODUCTION_PERSISTENCE.md): recommended persistence architecture for production bot deploys
- [DOCKER_POSTGRES_DEPLOY.md](DOCKER_POSTGRES_DEPLOY.md): run the Discord bot with Docker and Postgres
- [BACKUP_AND_RESTORE_DATABASE.md](BACKUP_AND_RESTORE_DATABASE.md): backup and restore flow for the Dockerized Postgres database
- [DEPENDENCY_MAINTENANCE.md](DEPENDENCY_MAINTENANCE.md): dependency upgrade workflow, tooling, and validation checklist
- [BUILD_GUIDE.md](BUILD_GUIDE.md): Windows executable build flow
- [ARCHITECTURE.md](ARCHITECTURE.md): architecture overview and layer map
- [BOT_DESKTOP_HTTP_CONTRACT.md](BOT_DESKTOP_HTTP_CONTRACT.md): explicit HTTP wire contract between the Desktop App and the bot runtime
- [ENGINEERING_REFERENCES.md](ENGINEERING_REFERENCES.md): books and engineering concepts that inform repository design decisions
- [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md): curated architecture diagrams grouped by layer and runtime
- [ARCHITECTURE_DIAGRAMS_GENERATED.md](ARCHITECTURE_DIAGRAMS_GENERATED.md): automatic `pyreverse` diagrams rendered as Mermaid in Markdown
- [RUNTIME_FLOWS.md](RUNTIME_FLOWS.md): bot and Desktop App entrypoints, composition roots, and main runtime flows
- [ARCHITECTURE_TRANSITIONS.md](ARCHITECTURE_TRANSITIONS.md): repository-specific examples for temporary facades, compatibility paths, and transition structure
- [README_DESKTOP_APP.md](README_DESKTOP_APP.md): desktop app guide
- [HOTKEY_SETUP.md](HOTKEY_SETUP.md): hotkey setup and usage

## Governance

- [../.specify/README.md](../.specify/README.md): canonical Spec Kit governance and workflow index
- [../.specify/memory/constitution.md](../.specify/memory/constitution.md): repository constitution and non-negotiable rules
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
- `docs/diagrams/` contains editable Mermaid architecture sources
- `docs/refactors/` contains incremental refactor plans and execution-oriented architecture improvements
- `.specify/` contains canonical project guidance and feature workflow templates
- AI/tool-specific instruction files should remain derivative of `.specify/`

## Navigation

- [Back to root README](../README.md)
