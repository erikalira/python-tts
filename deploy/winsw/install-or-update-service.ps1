[CmdletBinding()]
param(
    [switch]$SkipDependencyInstall,
    [switch]$SkipServiceRestart
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
$serviceExe = Join-Path $scriptDir "tts-discord-bot.exe"
$serviceXml = Join-Path $scriptDir "tts-discord-bot.xml"
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$envFile = Join-Path $repoRoot ".env"
$requirementsFile = Join-Path $repoRoot "requirements.txt"

function Test-ServiceInstalled {
    $service = Get-Service -Name "tts-discord-bot" -ErrorAction SilentlyContinue
    return $null -ne $service
}

Write-Host "Repository root: $repoRoot"

if (-not (Test-Path $serviceExe)) {
    throw "WinSW executable not found at '$serviceExe'. Download it and save it as tts-discord-bot.exe next to this script."
}

if (-not (Test-Path $serviceXml)) {
    throw "WinSW XML not found at '$serviceXml'."
}

if (-not (Test-Path $venvPython)) {
    throw "Virtual environment Python not found at '$venvPython'. Create .venv before running this script."
}

if (-not (Test-Path $envFile)) {
    throw "Environment file not found at '$envFile'. Create .env before running this script."
}

if (-not $SkipDependencyInstall) {
    Write-Host "Installing Python dependencies into .venv..."
    & $venvPython -m pip install -r $requirementsFile
}

if (Test-ServiceInstalled) {
    Write-Host "Stopping existing Windows service..."
    & $serviceExe stop

    Write-Host "Refreshing Windows service configuration..."
    & $serviceExe refresh
}
else {
    Write-Host "Installing Windows service..."
    & $serviceExe install
}

if (-not $SkipServiceRestart) {
    Write-Host "Starting Windows service..."
    & $serviceExe start
}
else {
    Write-Host "Service restart skipped by request."
}

Write-Host "Done."
