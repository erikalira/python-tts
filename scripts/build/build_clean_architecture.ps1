#!/usr/bin/env powershell
# Build TTS Hotkey with Clean Architecture for Windows
# This script creates a Windows executable with full clean architecture support

param(
    [switch]$Debug = $false,
    [switch]$SkipTests = $false
)

Write-Host "🏗️ Building TTS Hotkey with Clean Architecture..." -ForegroundColor Cyan
Write-Host "=================================================="

# Configuration
$AppName = "tts_hotkey_clean"
$MainScript = "tts_hotkey_configurable.py"
$DistPath = "dist"
$BuildPath = "build"
$SpecPath = "build\$AppName.spec"

# Check if running in correct directory
if (-not (Test-Path $MainScript)) {
    Write-Host "❌ Erro: $MainScript não encontrado!" -ForegroundColor Red
    Write-Host "Execute este script no diretório raiz do projeto" -ForegroundColor Yellow
    exit 1
}

# Check for Python
try {
    $PythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado no PATH!" -ForegroundColor Red
    exit 1
}

# Install/upgrade dependencies
Write-Host "`n🔧 Instalando dependências..." -ForegroundColor Yellow

$Dependencies = @(
    "pyinstaller>=5.0",
    "keyboard>=0.13.5",
    "requests>=2.25.0",
    "pyttsx3>=2.90",
    "gtts>=2.2.0",
    "pygame>=2.1.0",
    "pystray>=0.19.0",
    "pillow>=8.0.0"
)

foreach ($dep in $Dependencies) {
    Write-Host "📦 Instalando $dep..." -ForegroundColor Gray
    try {
        python -m pip install --upgrade $dep 2>&1 | Out-Null
        Write-Host "  ✅ $dep instalado" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️ Falha ao instalar $dep" -ForegroundColor Yellow
    }
}

# Run tests if not skipped
if (-not $SkipTests) {
    Write-Host "`n🧪 Executando testes de integração..." -ForegroundColor Yellow
    try {
        $TestResult = python test_integration.py
        Write-Host $TestResult
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️ Testes falharam, mas continuando build..." -ForegroundColor Yellow
        } else {
            Write-Host "✅ Testes passaram!" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️ Não foi possível executar testes" -ForegroundColor Yellow
    }
}

# Clean previous builds
Write-Host "`n🧹 Limpando builds anteriores..." -ForegroundColor Yellow
if (Test-Path $DistPath) {
    Remove-Item -Recurse -Force $DistPath
    Write-Host "✅ Pasta $DistPath limpa" -ForegroundColor Green
}
if (Test-Path $BuildPath) {
    Remove-Item -Recurse -Force $BuildPath
    Write-Host "✅ Pasta $BuildPath limpa" -ForegroundColor Green
}

# Build executable
Write-Host "`n🚀 Construindo executável..." -ForegroundColor Cyan

$PyInstallerArgs = @(
    "--name", $AppName,
    "--onefile",
    "--windowed",
    "--icon=icon.ico",
    "--add-data", "src;src",
    "--hidden-import", "keyboard",
    "--hidden-import", "requests",
    "--hidden-import", "pyttsx3",
    "--hidden-import", "pyttsx3.drivers",
    "--hidden-import", "pyttsx3.drivers.sapi5",
    "--hidden-import", "gtts",
    "--hidden-import", "gtts.tts",
    "--hidden-import", "pygame",
    "--hidden-import", "pygame.mixer",
    "--hidden-import", "pystray",
    "--hidden-import", "PIL",
    "--hidden-import", "PIL.Image",
    "--hidden-import", "PIL.ImageDraw",
    "--hidden-import", "tkinter",
    "--hidden-import", "tkinter.ttk",
    "--hidden-import", "tkinter.messagebox",
    "--hidden-import", "json",
    "--hidden-import", "threading",
    "--hidden-import", "pathlib",
    "--hidden-import", "dataclasses",
    "--hidden-import", "abc",
    "--hidden-import", "typing",
    $MainScript
)

if ($Debug) {
    $PyInstallerArgs += "--debug", "all"
    Write-Host "🔍 Modo debug ativado" -ForegroundColor Yellow
}

Write-Host "📋 Comando PyInstaller:" -ForegroundColor Gray
Write-Host "python -m PyInstaller $($PyInstallerArgs -join ' ')" -ForegroundColor Gray

try {
    & python -m PyInstaller @PyInstallerArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ BUILD CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Build falhou com código: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "`n❌ Erro durante o build: $_" -ForegroundColor Red
    exit 1
}

# Verify executable
$ExePath = Join-Path $DistPath "$AppName.exe"
if (Test-Path $ExePath) {
    $FileSize = [math]::Round((Get-Item $ExePath).Length / 1MB, 2)
    Write-Host "`n📊 Informações do executável:" -ForegroundColor Cyan
    Write-Host "  📍 Local: $ExePath" -ForegroundColor White
    Write-Host "  📏 Tamanho: $FileSize MB" -ForegroundColor White
    Write-Host "  📅 Criado: $((Get-Item $ExePath).CreationTime)" -ForegroundColor White
} else {
    Write-Host "`n❌ Executável não foi criado!" -ForegroundColor Red
    exit 1
}

# Create batch file
$BatchContent = @"
@echo off
cd /d "%~dp0"
echo.
echo 🎤 TTS Hotkey - Clean Architecture
echo ====================================
echo.
echo Iniciando aplicação...
echo.
"$AppName.exe"
if errorlevel 1 (
    echo.
    echo ❌ Erro na execução!
    pause
)
"@

$BatchPath = Join-Path $DistPath "run_$AppName.bat"
$BatchContent | Out-File -FilePath $BatchPath -Encoding ascii
Write-Host "  📄 Batch file: $BatchPath" -ForegroundColor White

Write-Host "`n🎉 BUILD FINALIZADO!" -ForegroundColor Green
Write-Host "=================================================="
Write-Host "📦 Executável: $ExePath" -ForegroundColor Cyan
Write-Host "🚀 Para executar: $BatchPath" -ForegroundColor Cyan
Write-Host "`n💡 RECURSOS INCLUSOS:" -ForegroundColor Yellow
Write-Host "  ✅ Clean Architecture completa" -ForegroundColor Green
Write-Host "  ✅ Interface gráfica (Tkinter)" -ForegroundColor Green  
Write-Host "  ✅ System Tray" -ForegroundColor Green
Write-Host "  ✅ Configuração persistente" -ForegroundColor Green
Write-Host "  ✅ TTS Multi-engine (gTTS + pyttsx3)" -ForegroundColor Green
Write-Host "  ✅ Discord Bot Integration" -ForegroundColor Green
Write-Host "  ✅ Hotkey Global ({} triggers)" -ForegroundColor Green
Write-Host "  ✅ Fallback automático" -ForegroundColor Green
Write-Host "`n🔧 CONFIGURAÇÃO:" -ForegroundColor Yellow
Write-Host "  1. Execute o .exe pela primeira vez" -ForegroundColor White
Write-Host "  2. Configure seu Discord User ID" -ForegroundColor White
Write-Host "  3. Use {}texto{} para falar!" -ForegroundColor White
Write-Host "`nPara suporte: https://github.com/erikalira/python-tts" -ForegroundColor Cyan