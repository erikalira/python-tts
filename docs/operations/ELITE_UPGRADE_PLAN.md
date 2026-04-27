# Elite Upgrade Implementation Plan

This plan turns the current repository into an elite-grade engineering baseline
through small, reversible changes. Each adjustment should be committed only
after the relevant validation passes. The Discord bot and the Windows hotkey
desktop app must continue to run independently after every phase.

## Current Baseline

Already present:

- Dependabot for GitHub Actions and Python dependencies in `.github/dependabot.yml`
- `pip-audit`, dependency review, and CodeQL in `.github/workflows/security.yml`
- Docker production image metadata labels in `Dockerfile`
- Docker Compose based local and production deployment flows
- Redis and Postgres integration test slices in `.github/workflows/test.yml`
- staging, rollback, release gates, disaster recovery, and production runbooks
  under `docs/deploy/` and `docs/operations/`
- a minimal `pyproject.toml` for Ruff configuration

Main gaps:

- no reproducible Python lockfile or package-manager-owned dependency model
- no SBOM generation or published SBOM artifact
- no Docker image vulnerability scan gate
- no GHCR image publish workflow with semantic-version tags
- no automated changelog or release note workflow
- no infrastructure-as-code baseline beyond Docker Compose
- no explicit `/speak` threat model covering auth, CORS, payload bounds, rate
  limiting, and token handling as one security story
- no dedicated contract, load, mutation, or dependency-failure chaos suites

## Chosen Upgrade Stack

Use these defaults unless a later ADR records a stronger operational reason to
change them:

- Python dependency manager and lockfile: `uv`
- IaC tool: OpenTofu
- SBOM format/tooling: CycloneDX
- Docker image vulnerability scanner: Trivy
- Image registry: GitHub Container Registry (GHCR)
- Release notes: GitHub generated release notes before stricter conventional
  commit enforcement
- Local and production baseline: Docker Compose remains the default until IaC
  or Kubernetes adoption is justified by runtime needs
- Local Kubernetes validation: Minikube is optional and validation-only
- Lightweight staging or production Kubernetes: k3s is preferred if Kubernetes
  becomes necessary
- Kubernetes customization: Kustomize before Helm unless templating pressure
  becomes real

## Commit And Validation Rule

Each implementation step should follow this loop:

1. Make one coherent adjustment with a narrow ownership boundary.
2. Run the fastest gate that covers the changed path.
3. Run the shared bot and desktop safety gate before commits that affect
   dependencies, CI, packaging, runtime wiring, HTTP contracts, or Docker.
4. Commit only after the selected gates pass.
5. Note any validation that cannot run locally in the commit message body or PR
   description.

Default local validation commands:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pyright
.\.venv\Scripts\python.exe -m pytest tests/unit tests/smoke --tb=short -v
```

Additional gates by area:

- Dependency or packaging changes: install from the chosen lockfile, then run
  `pip-audit` against the locked environment or exported requirements.
- Docker changes: build the image locally, run the container smoke check, and
  run the image scanner in CI.
- Redis/Postgres behavior: run the existing integration slices with the
  required service enabled.
- HTTP contract changes: run contract tests for `/speak` and bot health routes.
- Desktop runtime changes: run Windows smoke tests and manual desktop startup
  validation when GUI behavior is affected.

## Phase 1: Supply Chain Security

Goal: make dependency and artifact provenance auditable before changing release
automation.

1. Extend Dependabot if needed after packaging migration.
   - Affected files: `.github/dependabot.yml`, dependency config files
   - Validation: CI config lint by review, dependency PR dry-run if available
   - Commit: `chore: align dependency update automation`

2. Add SBOM generation.
   - Use CycloneDX for Python dependencies and Docker image SBOMs.
   - Publish SBOM artifacts from pull requests and release builds.
   - Affected files: `.github/workflows/security.yml`,
     `docs/operations/SECURITY_GATES.md`
   - Validation: security workflow runs and uploads SBOM artifacts
   - Commit: `ci: generate supply chain sboms`

3. Add Docker image vulnerability scanning.
   - Use Trivy because it supports GitHub Actions, SARIF, SBOMs, and image
     vulnerability scans with low workflow overhead.
   - Start with a non-blocking report, then promote high/critical findings to
     blocking once the baseline is clean.
   - Affected files: `.github/workflows/security.yml`, `Dockerfile`,
     `docs/operations/SECURITY_GATES.md`
   - Validation: scanner produces a CI artifact or SARIF upload
   - Commit: `ci: scan docker image vulnerabilities`

4. Add lockfile-based installs.
   - Use `uv` as the steady-state dependency and lockfile tool.
   - Keep `requirements.txt` only as an exported compatibility artifact if
     deployment still needs it.
   - Affected files: `pyproject.toml`, lockfile, requirements files,
     Dockerfile, CI workflows, docs
   - Validation: clean environment sync from lockfile, unit/smoke tests,
     Docker build
   - Commit: `build: use reproducible python dependency lock`

## Phase 2: Release Engineering

Goal: produce traceable, rollback-friendly releases for bot images and desktop
artifacts.

1. Publish versioned Docker images to GHCR.
   - Tag images with semantic version, Git SHA, branch alias, and `latest` only
     for stable releases.
   - Add OCI source, revision, version, and created labels.
   - Affected files: release workflow, `Dockerfile`, docs
   - Validation: dry-run build on PR, publish on tag
   - Commit: `ci: publish versioned bot images to ghcr`

2. Add semantic tag release workflow.
   - Trigger on tags like `vMAJOR.MINOR.PATCH`.
   - Build and attach desktop artifacts where applicable.
   - Reuse the same test gates as pull requests before publish.
   - Affected files: `.github/workflows/release.yml`, docs
   - Validation: workflow dry-run on `workflow_dispatch`, tag release test in a
     disposable branch if needed
   - Commit: `ci: add semantic release pipeline`

3. Add automated changelog.
   - Use GitHub generated release notes first.
   - Document commit categories before enforcing conventional commits.
   - Affected files: release workflow, `docs/operations/RELEASE_CHECKLIST.md`,
     optional changelog config
   - Validation: generated changelog preview artifact
   - Commit: `docs: standardize changelog generation`

4. Automate rollback.
   - Convert the existing rollback documentation into an operator workflow that
     can redeploy a previous GHCR image tag.
   - Keep the manual runbook as the source of operational checks.
   - Affected files: `.github/workflows/rollback.yml`,
     `docs/deploy/STAGING_AND_ROLLBACK.md`,
     `docs/operations/DR_DRILLS.md`
   - Validation: workflow dry-run against staging or local compose equivalent
   - Commit: `ci: automate image rollback workflow`

## Phase 3: Runtime Security

Goal: make `/speak` safe if exposed beyond a trusted local network.

1. Write the threat model.
   - Cover assets, actors, trust boundaries, abuse cases, tokens/secrets, Redis,
     Postgres, Discord bot token, desktop-to-bot HTTP calls, and logs.
   - Affected files: `docs/security/THREAT_MODEL.md`, `docs/README.md`
   - Validation: documentation review against current runtime flows
   - Commit: `docs: document runtime threat model`

2. Make CORS explicit.
   - Default to deny or a configured allowlist.
   - Keep local desktop use ergonomic through configuration, not hard-coded
     broad origins.
   - Affected files: bot HTTP adapter/config, environment docs, tests
   - Validation: HTTP contract tests
   - Commit: `security: enforce explicit speak cors policy`

3. Add `/speak` authentication and rate limiting.
   - Prefer a simple shared token or signed request first, then evolve if the
     endpoint becomes multi-user.
   - Rate limit by token or source with clear rejection responses.
   - Affected files: presentation bot HTTP layer, application contracts where
     needed, config docs, tests
   - Validation: unit, contract, and bot smoke tests
   - Commit: `security: protect speak endpoint`

4. Tighten payload limits and validation.
   - Enforce request body size, text length, content type, JSON shape, and queue
     backpressure behavior.
   - Return typed error responses that desktop code can handle.
   - Affected files: HTTP contracts, bot presentation layer, desktop client if
     response handling changes
   - Validation: contract tests, desktop smoke tests
   - Commit: `security: bound speak request payloads`

## Phase 4: Advanced Test Coverage

Goal: cover the behavior that breaks most expensively in production.

1. Add HTTP contract tests.
   - Encode the documented bot-desktop wire contract for success, auth failure,
     validation failure, rate limit, queue failure, and health checks.
   - Affected files: `tests/contract/`, HTTP contract docs
   - Validation: contract suite in CI
   - Commit: `test: add bot desktop http contract tests`

2. Add realistic desktop-to-bot E2E.
   - Exercise desktop request construction through the bot endpoint without
     requiring Discord voice connectivity.
   - Use fake TTS/queue adapters where needed to keep the test deterministic.
   - Affected files: `tests/e2e/`, desktop runtime wiring tests
   - Validation: E2E suite on Windows CI or marked local-only with a clear gate
   - Commit: `test: cover desktop to bot speak flow`

3. Add queue load tests.
   - Start with a bounded pytest benchmark or Locust/k6 script that targets
     queue throughput, latency, and backpressure.
   - Affected files: `tests/load/` or `scripts/load/`, operations docs
   - Validation: non-blocking CI artifact first; blocking threshold later
   - Commit: `test: add queue load baseline`

4. Add mutation testing for critical domain behavior.
   - Scope to pure core/application modules first to avoid slow runtime tests.
   - Use a small threshold and raise it only after baseline triage.
   - Affected files: mutation config, docs, CI optional job
   - Validation: mutation job report
   - Commit: `test: add mutation baseline for core behavior`

5. Add dependency-failure chaos tests.
   - Cover Redis unavailable, Postgres unavailable, queue reconnect behavior,
     startup validation failures, and degradation messages.
   - Affected files: integration tests, runbooks
   - Validation: integration suites with services intentionally stopped or
     misconfigured
   - Commit: `test: cover dependency failure modes`

## Phase 5: Infrastructure As Code

Goal: describe environments explicitly without forcing Kubernetes before it is
operationally justified.

1. Add an environment inventory and IaC decision record.
   - Decide what must exist in dev, staging, and production.
   - Keep Docker Compose as the local runtime baseline.
   - Affected files: ADR, `docs/deploy/ENVIRONMENTS.md`
   - Validation: docs review against existing deploy scripts
   - Commit: `docs: define infrastructure environments`

2. Add OpenTofu skeleton.
   - Start with variables, providers, remote-state decision, and modules for
     secrets, compute target, Postgres, Redis, and observability endpoints.
   - Keep secrets out of state where the provider allows it.
   - Affected files: `infra/`, docs
   - Validation: `tofu fmt`, `tofu validate` or equivalent
   - Commit: `infra: add opentofu environment skeleton`

3. Add optional Kubernetes manifests.
   - Add Kustomize overlays before Helm unless templating pressure is real.
   - Use Minikube only for local manifest validation.
   - Target k3s or a small managed cluster profile only after image publishing
     and rollback automation exist.
   - Affected files: `deploy/k8s/`, docs
   - Validation: `kubectl kustomize`, schema validation
   - Commit: `infra: add kustomize deployment manifests`

## Phase 6: Python Packaging And Developer Commands

Goal: make local, CI, Docker, and release installs converge on one dependency
and command model.

1. Expand `pyproject.toml` into the project metadata source.
   - Move runtime and test dependencies into grouped dependency sections.
   - Preserve console entrypoints only if they clarify bot and desktop startup.
   - Affected files: `pyproject.toml`, requirements files, docs
   - Validation: package install, unit/smoke tests
   - Commit: `build: move python metadata to pyproject`

2. Add standardized commands.
   - Prefer a `Makefile` plus PowerShell-friendly script aliases if Windows
     ergonomics require them.
   - Include `make test`, `make lint`, `make typecheck`, `make security`,
     `make ci`, and `make docker-build`.
   - Affected files: `Makefile`, `scripts/`, docs
   - Validation: each command runs locally
   - Commit: `build: add standard developer commands`

3. Make Docker and CI consume the lockfile.
   - Remove permanent dual dependency flows once deployment no longer needs
     loose requirements.
   - Affected files: Dockerfile, CI workflows, dependency docs
   - Validation: CI, Docker build, runtime smoke tests
   - Commit: `build: align docker and ci dependency installs`

## Recommended Execution Order

1. Documentation-only truth alignment: this plan, docs index, and current status.
2. SBOM and Docker scanning, because they are additive and low risk.
3. Lockfile and `pyproject.toml` migration, because it affects every later CI
   and release step.
4. GHCR image publish and semantic release workflow.
5. Threat model, CORS, auth, payload bounds, and contract tests.
6. Advanced reliability tests: E2E, load, mutation, and chaos.
7. IaC skeleton and optional Kubernetes manifests.
8. Rollback automation once versioned images and environments exist.

## Non-Goals For The First Pass

- Do not introduce Kubernetes before versioned images and rollback are working.
- Do not make mutation or load testing block every PR until baseline noise is
  understood.
- Do not create a broad authentication framework for a single internal endpoint
  unless exposure requirements change.
- Do not keep both loose requirements and lockfile installs as permanent equal
  paths; choose one steady state and document any temporary compatibility.
