# Architecture Transitions

This guide complements the canonical transition rule in
`.specify/transition-cleanup.md` with repository-specific architectural
examples.

## Typical transition shapes in this repository

- facade modules that preserve stable imports while use cases move between
  `src/application/` modules
- compatibility adapters that keep one runtime working while shared logic is
  extracted from `src/desktop/`
- temporary bridges between old mapping-style payloads and newer explicit
  contracts
- narrow wrappers around provider or transport code during adapter cleanup

## Where transitions usually belong

- shared contract migrations: `src/application/`
- provider or IO migrations: `src/infrastructure/`
- desktop runtime migrations: `src/desktop/`
- presentation migrations: `src/presentation/`

Avoid spreading the same transition behavior across multiple layers.

## Good repository-specific examples

- re-exporting moved use cases while callers migrate to a new application module
- keeping one runtime adapter temporarily while shared orchestration is extracted
- preserving a narrow compatibility layer for tests during a contract migration

## Bad repository-specific examples

- keeping duplicate desktop and shared implementations after extraction is done
- leaving mapping-style compatibility in multiple layers after a typed contract exists
- adding a facade that hides ownership instead of clarifying migration steps

## How to use this guide

Use `.specify/transition-cleanup.md` for the rule and removal criteria.
Use this file when you want concrete architecture examples tied to this
repository's layers and runtime structure.
