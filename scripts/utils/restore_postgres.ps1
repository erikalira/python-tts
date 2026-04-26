param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,
    [string]$ContainerName = "tts-bot-postgres",
    [string]$DatabaseName = "tts_hotkey_windows",
    [string]$DatabaseUser = $(if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "tts_user" })
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $BackupFile)) {
    throw "Backup file not found: $BackupFile"
}

$fileName = Split-Path -Leaf $BackupFile
$containerBackupPath = "/tmp/$fileName"

Write-Host "Copying backup '$BackupFile' into container '$ContainerName'..."
docker cp $BackupFile "${ContainerName}:$containerBackupPath"

Write-Host "Restoring database '$DatabaseName'..."
docker exec $ContainerName pg_restore -U $DatabaseUser -d $DatabaseName --clean --if-exists $containerBackupPath

Write-Host "Cleaning temporary restore file inside container..."
docker exec $ContainerName rm $containerBackupPath

Write-Host "Restore complete."
