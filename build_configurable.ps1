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

# Instalar dependencias automaticamente
Write-Host "INSTALANDO DEPENDENCIAS..." -ForegroundColor Green

# Verificar se requirements.txt existe
if (Test-Path "requirements.txt") {
    Write-Host "Instalando requirements.txt..." -ForegroundColor Yellow
    try {
        & python -m pip install -r requirements.txt
        Write-Host "Requirements instalados com sucesso!" -ForegroundColor Green
    } catch {
        Write-Host "ERRO ao instalar requirements!" -ForegroundColor Red
        Write-Host "Verifique se python esta disponivel" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "requirements.txt nao encontrado - instalando dependencias basicas..." -ForegroundColor Yellow
}

# Instalar PyInstaller usando python -m pip
Write-Host "Verificando PyInstaller..." -ForegroundColor Yellow
try {
    $pyinstaller_check = & python -m PyInstaller --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PyInstaller ja instalado: $pyinstaller_check" -ForegroundColor Green
    } else {
        throw "PyInstaller nao encontrado"
    }
} catch {
    Write-Host "Instalando PyInstaller..." -ForegroundColor Yellow
    try {
        & python -m pip install pyinstaller
        Write-Host "PyInstaller instalado com sucesso!" -ForegroundColor Green
    } catch {
        Write-Host "ERRO ao instalar PyInstaller!" -ForegroundColor Red
        Write-Host "Execute manualmente: python -m pip install pyinstaller" -ForegroundColor Yellow
        exit 1
    }
}

# Verificar novamente se PyInstaller funciona
Write-Host "Testando PyInstaller..." -ForegroundColor Yellow
try {
    $final_check = & python -m PyInstaller --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PyInstaller funcionando: $final_check" -ForegroundColor Green
    } else {
        throw "PyInstaller nao responde"
    }
} catch {
    Write-Host "ERRO: PyInstaller nao esta funcionando!" -ForegroundColor Red
    Write-Host "Tentando via python -c..." -ForegroundColor Yellow
    
    # Teste alternativo
    try {
        & python -c "import PyInstaller; print('PyInstaller OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "PyInstaller importado com sucesso!" -ForegroundColor Green
        } else {
            throw "Falha na importacao"
        }
    } catch {
        Write-Host "ERRO CRITICO: PyInstaller nao pode ser usado!" -ForegroundColor Red
        Write-Host "Solucoes:" -ForegroundColor Yellow
        Write-Host "1. python -m pip install --upgrade pyinstaller" -ForegroundColor White
        Write-Host "2. Reiniciar terminal/PowerShell" -ForegroundColor White
        Write-Host "3. Verificar PATH do Python" -ForegroundColor White
        exit 1
    }
}

Write-Host "Todas as dependencias verificadas!" -ForegroundColor Green
Write-Host

# Confirmar build
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

# Comando PyInstaller usando python -m
Write-Host "Executando PyInstaller via python -m..." -ForegroundColor Yellow

$pyinstaller_cmd = @(
    "python", "-m", "PyInstaller",
    "--onefile",
    "--windowed", 
    "--name=tts_hotkey_premium",
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
    & @pyinstaller_cmd

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
        throw "Arquivo executavel nao foi criado"
    }
    
} catch {
    Write-Host
    Write-Host "ERRO NO BUILD!" -ForegroundColor Red
    Write-Host "Detalhes: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host
    Write-Host "SOLUCOES:" -ForegroundColor Yellow
    Write-Host "   1. python -m pip install --upgrade pyinstaller" -ForegroundColor White
    Write-Host "   2. Reiniciar PowerShell como Administrador" -ForegroundColor White
    Write-Host "   3. Verificar antivirus (pode bloquear)" -ForegroundColor White
    Write-Host "   4. Testar: python -c 'import PyInstaller'" -ForegroundColor White
    exit 1
}

Write-Host "Build Premium concluido!" -ForegroundColor Magenta