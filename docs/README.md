# Documentation

This directory contains the repository's supporting documentation. The root
`README.md` stays short on purpose, while the details live here.

## Main guides

- [SETUP.md](SETUP.md): ambiente virtual, instalacao e ativacao no Windows e Linux
- [TESTING.md](TESTING.md): automated test structure and local execution
- [ENVIRONMENTS.md](ENVIRONMENTS.md): local and production environment variables for bot and Desktop App
- [WINDOWS_BOT_SERVICE.md](WINDOWS_BOT_SERVICE.md): WinSW deployment guide for keeping the Discord bot running as a Windows service
- [DEPENDENCY_MAINTENANCE.md](DEPENDENCY_MAINTENANCE.md): dependency upgrade workflow, tooling, and validation checklist
- [BUILD_GUIDE.md](BUILD_GUIDE.md): Windows executable build flow
- [ARCHITECTURE.md](ARCHITECTURE.md): architecture overview and layer map
- [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md): curated architecture diagrams grouped by layer and runtime
- [ARCHITECTURE_DIAGRAMS_GENERATED.md](ARCHITECTURE_DIAGRAMS_GENERATED.md): automatic `pyreverse` diagrams rendered as Mermaid in Markdown
- [RUNTIME_FLOWS.md](RUNTIME_FLOWS.md): bot and Desktop App entrypoints, composition roots, and main runtime flows
- [ARCHITECTURE_TRANSITIONS.md](ARCHITECTURE_TRANSITIONS.md): guidance for temporary facades, compatibility paths, and steady-state cleanup
- [CHANGE_MAP.md](CHANGE_MAP.md): where to start for bot, desktop, shared, refactor, and documentation changes
- [REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md): short checklist for review quality, contracts, and runtime safety
- [TRANSITION_CLEANUP.md](TRANSITION_CLEANUP.md): operational rule for removing temporary compatibility code
- [CHANGE_EXAMPLES.md](CHANGE_EXAMPLES.md): examples of where to start and where code should live
- [README_DESKTOP_APP.md](README_DESKTOP_APP.md): desktop app guide
- [HOTKEY_SETUP.md](HOTKEY_SETUP.md): hotkey setup and usage

## Governance

- [../.specify/README.md](../.specify/README.md): canonical Spec Kit governance and workflow index
- [../.specify/memory/constitution.md](../.specify/memory/constitution.md): repository constitution and non-negotiable rules
- [../.specify/templates/spec-template.md](../.specify/templates/spec-template.md): feature specification standard
- [../.specify/templates/plan-template.md](../.specify/templates/plan-template.md): implementation plan standard
- [../.specify/templates/tasks-template.md](../.specify/templates/tasks-template.md): task breakdown standard

## Conventions

- `docs/` contains durable architecture and operational guides
- `docs/diagrams/` contains editable Mermaid architecture sources
- `docs/features/` contains feature docs, feature iterations, and implementation notes
- `docs/refactors/` contains incremental refactor plans and execution-oriented architecture improvements
- `.specify/` contains canonical project guidance and feature workflow templates

## Features

- [features/README.md](features/README.md): feature documentation index
- [features/DESKTOP_APP_ARCHITECTURE_REFACTOR_PLAN.md](features/DESKTOP_APP_ARCHITECTURE_REFACTOR_PLAN.md): desktop architecture review and refactor execution log
- [features/DESKTOP_APP_GUI_UX.md](features/DESKTOP_APP_GUI_UX.md): desktop GUI UX and responsiveness
- [features/DESKTOP_APP_MAIN_PANEL.md](features/DESKTOP_APP_MAIN_PANEL.md): desktop main panel flow and manual checks
- [features/INTERFACE_CONFIGURACAO.md](features/INTERFACE_CONFIGURACAO.md): configuration interface details
- [features/VOICE_TIMEOUT.md](features/VOICE_TIMEOUT.md): voice timeout behavior
- [features/ICON_TROUBLESHOOTING.md](features/ICON_TROUBLESHOOTING.md): icon troubleshooting
- [features/DISCORD_RATE_LIMIT_SOLUTION.md](features/DISCORD_RATE_LIMIT_SOLUTION.md): rate limit notes
- [features/MULTI_SERVER_IMPROVEMENTS.md](features/MULTI_SERVER_IMPROVEMENTS.md): multi-server improvements
- [features/SISTEMA_CONEXAO_INTELIGENTE.md](features/SISTEMA_CONEXAO_INTELIGENTE.md): connection flow details

## Navigation

- [Back to root README](../README.md)
