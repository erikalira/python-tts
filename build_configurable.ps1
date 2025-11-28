# Build Script Premium para TTS Hotkey
# Versao corrigida - PowerShell compativel

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "BUILD TTS HOTKEY PREMIUM" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host

# Verificar se o arquivo existe
if (-not (Test-Path "tts_hotkey_configurable.py")) {
    Write-Host "ERRO: Arquivo tts_hotkey_configurable.py nao encontrado!" -ForegroundColor Red
    Write-Host "Certifique-se de que esta no diretorio correto" -ForegroundColor Yellow
    exit 1
}

Write-Host "ANALISANDO CONFIGURACAO..." -ForegroundColor Green

# Ler configurações (método mais simples)
$config_content = Get-Content "tts_hotkey_configurable.py" -Raw -Encoding UTF8

# Extrair configurações principais
$discord_url = ""
$trigger_open = ""
$trigger_close = ""
$tts_rate = ""

# Procurar Discord URL
if ($config_content -match 'DISCORD_BOT_URL\s*=\s*"([^"]+)"') {
    $discord_url = $matches[1]
}

# Procurar triggers
if ($config_content -match 'TRIGGER_OPEN\s*=\s*"([^"]+)"') {
    $trigger_open = $matches[1]
}

if ($config_content -match 'TRIGGER_CLOSE\s*=\s*"([^"]+)"') {
    $trigger_close = $matches[1]
}

# Procurar TTS rate
if ($config_content -match 'TTS_RATE\s*=\s*(\d+)') {
    $tts_rate = $matches[1]
}

Write-Host "CONFIGURACAO DETECTADA:" -ForegroundColor Cyan
Write-Host "   Discord Bot: $discord_url" -ForegroundColor White
Write-Host "   Triggers: '$trigger_open' e '$trigger_close'" -ForegroundColor White
Write-Host "   TTS Rate: $tts_rate" -ForegroundColor White
Write-Host

# Verificar se PyInstaller esta instalado
Write-Host "VERIFICANDO DEPENDENCIAS..." -ForegroundColor Green

try {
    $pyinstaller_check = & pyinstaller --version 2>&1
    Write-Host "PyInstaller: $pyinstaller_check" -ForegroundColor Green
} catch {
    Write-Host "PyInstaller nao encontrado!" -ForegroundColor Red
    Write-Host "INSTALAR: pip install pyinstaller" -ForegroundColor Yellow
    exit 1
}

# Confirmar build
Write-Host
Write-Host "PRONTO PARA COMPILAR!" -ForegroundColor Yellow
Write-Host "Resultado: dist/tts_hotkey_premium.exe" -ForegroundColor Cyan
Write-Host
$confirm = Read-Host "Continuar? (s/N)"

if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host "Build cancelado." -ForegroundColor Red
    exit 0
}

Write-Host
Write-Host "COMPILANDO..." -ForegroundColor Yellow

# Limpar builds anteriores
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Comando PyInstaller otimizado
$pyinstaller_args = @(
    "--onefile",
    "--windowed",
    "--name=tts_hotkey_premium",
    "--icon=icon.ico",
    "--add-data=*.py;.",
    "--hidden-import=pystray",
    "--hidden-import=PIL",
    "--hidden-import=PIL._tkinter_finder",
    "--hidden-import=pyttsx3",
    "--hidden-import=pyttsx3.drivers",
    "--hidden-import=pyttsx3.drivers.sapi5",
    "--hidden-import=requests",
    "--hidden-import=keyboard",
    "--collect-all=pyttsx3",
    "tts_hotkey_configurable.py"
)

try {
    & pyinstaller @pyinstaller_args

    if (Test-Path "dist/tts_hotkey_premium.exe") {
        Write-Host
        Write-Host "BUILD CONCLUIDO COM SUCESSO!" -ForegroundColor Green
        Write-Host "=" * 60 -ForegroundColor Cyan
        
        $file_size = (Get-Item "dist/tts_hotkey_premium.exe").Length
        $size_mb = [math]::Round($file_size / 1MB, 2)
        
        Write-Host "RESULTADO:" -ForegroundColor Cyan
        Write-Host "   Arquivo: dist/tts_hotkey_premium.exe" -ForegroundColor White
        Write-Host "   Tamanho: $size_mb MB" -ForegroundColor White
        Write-Host "   Configuracao: Integrada" -ForegroundColor Green
        Write-Host
        Write-Host "RECURSOS INCLUIDOS:" -ForegroundColor Green
        Write-Host "   - Discord Bot: $discord_url" -ForegroundColor White
        Write-Host "   - Triggers: '$trigger_open$trigger_close'" -ForegroundColor White
        Write-Host "   - TTS Rate: $tts_rate" -ForegroundColor White
        Write-Host "   - Todas as dependencias" -ForegroundColor White
        Write-Host "   - Zero arquivos externos" -ForegroundColor White
        Write-Host
        Write-Host "PRONTO PARA USO!" -ForegroundColor Yellow
        Write-Host "=" * 60 -ForegroundColor Cyan
        
    } else {
        throw "Arquivo executável não foi criado"
    }
    
} catch {
    Write-Host
    Write-Host "ERRO NO BUILD!" -ForegroundColor Red
    Write-Host "Detalhes: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host
    Write-Host "SOLUCOES:" -ForegroundColor Yellow
    Write-Host "   1. Instalar dependencias: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "   2. Atualizar PyInstaller: pip install --upgrade pyinstaller" -ForegroundColor White
    Write-Host "   3. Executar como Administrador" -ForegroundColor White
    Write-Host "   4. Verificar antivirus (pode bloquear)" -ForegroundColor White
    exit 1
}

Write-Host "Build Premium concluido!" -ForegroundColor Magenta