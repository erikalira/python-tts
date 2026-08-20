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
- The Docker image is scanned with Trivy. Critical image vulnerabilities are a
  blocking gate. High vulnerabilities remain a documented follow-up threshold
  until the baseline is clean enough to promote `HIGH,CRITICAL` to blocking.
- The `Release` workflow repeats the runtime dependency audit and scans the
  published image digest before signing it. Both audits carry the documented
  exception listed under Accepted Vulnerability Exceptions.
- Release images are signed with Cosign keyless signing and receive a GitHub
  build provenance attestation pushed to the registry.
- The OpenSSF Scorecard workflow runs on `main`, weekly, and manually. It
  publishes SARIF and remains report-only until a stable project score baseline
  is recorded.

## Accepted Vulnerability Exceptions

An exception is recorded here only when there is no resolvable upgrade and the
flaw is not reachable from either runtime. Each one is re-evaluated whenever its
blocking constraint changes.

| ID | Package | Status |
| --- | --- | --- |
| `PYSEC-2026-2132` | `click < 8.3.3` | Accepted. No upgrade path |

`gtts 2.5.4`, the latest released version, pins `click<8.2`, so the fixed
`click 8.3.3` cannot be resolved while `gtts` is a runtime dependency. The flaw
is a command injection in `click.edit()`, which opens an interactive editor.
This repository never imports `click`, and `gtts` uses it only in its own CLI
(`gtts/cli.py`), which neither the bot nor the Desktop App invokes.

The exception is applied with `pip-audit --ignore-vuln PYSEC-2026-2132` in the
`Security` workflow, the `Release` workflow, and the `security` Makefile target.
Remove the flag once `gtts` relaxes the constraint, and re-run the audit to
confirm the finding is gone rather than merely re-suppressed.

## Artifact Verification

For a released image, verify the keyless signature and build provenance before
promoting the tag:

```bash
cosign verify \
  --certificate-identity-regexp "https://github.com/.*/.github/workflows/release.yml@refs/tags/.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/<owner>/tts-hotkey-windows-bot@sha256:<digest>

gh attestation verify \
  oci://ghcr.io/<owner>/tts-hotkey-windows-bot@sha256:<digest> \
  --repo <owner>/tts-hotkey-windows
```

Download the CycloneDX SBOM artifacts from the `Security` workflow or use the
Buildx registry SBOM attached during release for registry-native inspection.

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
- confirm the Trivy critical vulnerability gate passed
- verify the Cosign signature and build provenance for the selected image digest
- review OpenSSF Scorecard output and record any newly accepted risk
- run the dependency maintenance validation flow when requirements changed
- check `docs/operations/RELEASE_CHECKLIST.md` for observability and rollback
  gates
- record any skipped runtime validation as an explicit release gap

