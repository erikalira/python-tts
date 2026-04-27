param(
    [Parameter(Position = 0)]
    [ValidateSet("sync", "lint", "typecheck", "test", "security", "ci", "docker-build", "kustomize")]
    [string]$Task = "ci"
)

$ErrorActionPreference = "Stop"

if (-not $env:UV_PROJECT_ENVIRONMENT) {
    $env:UV_PROJECT_ENVIRONMENT = ".test-artifacts/uv-venv"
}

if (-not $env:PYTHONPATH) {
    $env:PYTHONPATH = (Get-Location).Path
}

function Invoke-Uv {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & uv @Arguments
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

function Invoke-DockerBuild {
    $shortSha = (& git rev-parse --short HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    & docker build --build-arg APP_VERSION=local --build-arg "VCS_REF=$shortSha" -t tts-hotkey-windows-bot:local .
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

function Invoke-KustomizeValidation {
    foreach ($overlay in @("minikube", "staging", "prod")) {
        & kubectl kustomize "deploy/k8s/overlays/$overlay" | Out-Null
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }
}

switch ($Task) {
    "sync" {
        Invoke-Uv sync --locked --group test
    }
    "lint" {
        Invoke-Uv run --group test ruff check .
    }
    "typecheck" {
        Invoke-Uv run --group test pyright
    }
    "test" {
        $env:CI = "true"
        Invoke-Uv run --group test pytest tests/unit tests/contract tests/e2e tests/chaos tests/smoke --tb=short -v
    }
    "security" {
        Invoke-Uv run --group security pip-audit
    }
    "ci" {
        & $PSCommandPath lint
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & $PSCommandPath typecheck
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & $PSCommandPath test
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    "docker-build" {
        Invoke-DockerBuild
    }
    "kustomize" {
        Invoke-KustomizeValidation
    }
}
