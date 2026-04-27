# Security Gates

This guide documents the repository's minimum security gates for dependency and
runtime-entrypoint changes.

## Automated Gates

- Dependabot opens weekly PRs for `uv.lock` and GitHub Actions.
- The `Security` GitHub Actions workflow runs `pip-audit` against
  `requirements.txt` and `requirements-test.txt` using tooling installed from
  the locked `security` dependency group.
- Pull requests run GitHub dependency review when dependency manifests change.
- CodeQL scans Python on pull requests, pushes to `main`, scheduled runs, and
  manual dispatch.
- The `Security` workflow generates CycloneDX SBOM artifacts for runtime
  Python dependencies, test Python dependencies, and the Docker image.
- The Docker image is scanned with Trivy for high and critical vulnerabilities.
  The first gate is intentionally non-blocking while the repository establishes
  a clean baseline; promote it to blocking by changing the Trivy `exit-code`
  once baseline findings are triaged.

## Runtime Entry Points

- Bot `/speak` entrypoints are rate-limited per guild and caller by default.
- Configure `BOT_RATE_LIMIT_MAX_REQUESTS` and
  `BOT_RATE_LIMIT_WINDOW_SECONDS` in bot environments.
- Set `BOT_RATE_LIMIT_MAX_REQUESTS=0` only for local troubleshooting, and
  restore the default before release.
- Rate-limit failures must be visible in logs, and HTTP `/speak` failures must
  set span attributes when OpenTelemetry is enabled.

## Release Expectations

Before a release that changes dependencies, bot entrypoints, HTTP presentation,
or runtime configuration:

- confirm the `Security` workflow is green
- download and archive the CycloneDX SBOM artifacts for release traceability
- review the Trivy Docker image scan artifact and record any accepted risk
- run the dependency maintenance validation flow when requirements changed
- check `docs/operations/RELEASE_CHECKLIST.md` for observability and rollback
  gates
- record any skipped runtime validation as an explicit release gap

