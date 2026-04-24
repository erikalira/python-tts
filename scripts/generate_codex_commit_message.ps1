$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$stagedDiff = git diff --cached --no-ext-diff --unified=3

if ([string]::IsNullOrWhiteSpace($stagedDiff)) {
    Write-Error "No staged changes found. Stage your changes first and run the command again."
}

$outputFile = Join-Path $env:TEMP "codex-last-commit-message.txt"
$prompt = @"
Generate a single git commit subject line for the staged changes.

Requirements:
- Output only the commit subject.
- Use Conventional Commits style.
- Use English.
- Keep it under 72 characters.
- Base it only on the staged diff provided in <stdin>.
"@

$stagedDiff |
    codex exec `
        --sandbox read-only `
        --color never `
        --output-last-message $outputFile `
        $prompt | Out-Host

if (-not (Test-Path $outputFile)) {
    Write-Error "Codex did not return a commit message."
}

$message = (Get-Content $outputFile -Raw).Trim()

if ([string]::IsNullOrWhiteSpace($message)) {
    Write-Error "Codex returned an empty commit message."
}

Set-Clipboard -Value $message

Write-Host ""
Write-Host "Commit message copied to clipboard:"
Write-Host $message
