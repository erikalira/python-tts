param(
    [string]$ContainerName = "tts-bot-postgres",
    [string]$DatabaseName = "tts_hotkey_windows",
    [string]$DatabaseUser = $(if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "tts_user" }),
    [string]$BackupDirectory = "C:\Backups\tts-bot",
    [int]$RetentionDays = 30
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path $BackupDirectory | Out-Null

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$fileName = "tts_backup_$timestamp.dump"
$hostBackupPath = Join-Path $BackupDirectory $fileName
$containerBackupPath = "/tmp/$fileName"

Write-Host "Creating backup from container '$ContainerName'..."
docker exec $ContainerName pg_dump -U $DatabaseUser -d $DatabaseName -Fc -f $containerBackupPath

Write-Host "Copying backup to '$hostBackupPath'..."
docker cp "${ContainerName}:$containerBackupPath" $hostBackupPath

Write-Host "Cleaning temporary backup file inside container..."
docker exec $ContainerName rm $containerBackupPath

Write-Host "Removing local backups older than $RetentionDays day(s)..."
$cutoff = (Get-Date).AddDays(-$RetentionDays)
Get-ChildItem -Path $BackupDirectory -Filter "*.dump" -File |
    Where-Object { $_.LastWriteTime -lt $cutoff } |
    Remove-Item -Force

Write-Host "Backup complete: $hostBackupPath"
