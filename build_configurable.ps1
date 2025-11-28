# 🎯 TTS Hotkey - Build Script Configurável (Versão Premium)

Write-Host ""
Write-Host "=" * 70
Write-Host "🎯 TTS HOTKEY - COMPILADOR INTELIGENTE" -ForegroundColor Cyan
Write-Host "=" * 70
Write-Host ""

$config_file = "tts_hotkey_configurable.py"

# Verificar se arquivo existe
if (-not (Test-Path $config_file)) {
    Write-Host "❌ Arquivo $config_file não encontrado!" -ForegroundColor Red
    Write-Host "   Certifique-se de estar no diretório correto."
    Read-Host "   Pressione Enter para sair"
    exit 1
}

# Mostrar configuração atual
Write-Host "🔍 ANALISANDO CONFIGURAÇÃO ATUAL..." -ForegroundColor Yellow
Write-Host ""

try {
    $config_content = Get-Content $config_file -Raw
    
    # Extrair configurações básicas
    if ($config_content -match 'DISCORD_BOT_URL = "([^"]*)"') {
        $discord_url = $matches[1]
        Write-Host "🌐 Discord Bot: $discord_url" -ForegroundColor Green
    }
    
    if ($config_content -match 'TTS_LANGUAGE = "([^"]*)"') {
        $language = $matches[1]
        Write-Host "🎤 Idioma TTS: $language" -ForegroundColor Green
    }
    
    if ($config_content -match 'TTS_RATE = (\d+)') {
        $rate = $matches[1]
        Write-Host "⚡ Velocidade: $rate wpm" -ForegroundColor Green
    }
    
    if ($config_content -match 'TRIGGER_OPEN = "([^"]*)"') {
        $trigger_open = $matches[1]
        if ($config_content -match 'TRIGGER_CLOSE = "([^"]*)"') {
            $trigger_close = $matches[1]
            Write-Host "⌨️ Triggers: '$trigger_open'texto'$trigger_close'" -ForegroundColor Green
        }
    }
    
    Write-Host ""
} catch {
    Write-Host "⚠️ Não foi possível analisar as configurações" -ForegroundColor Yellow
}

# Confirmar antes de compilar
Write-Host "📋 PRONTO PARA COMPILAR!" -ForegroundColor Cyan
Write-Host "   ✅ Configuração personalizada detectada"
Write-Host "   ✅ Arquivo fonte encontrado"
Write-Host "   🎯 Resultado: Um único .exe standalone"
Write-Host ""

$confirmation = Read-Host "Continuar com a compilação? (S/n)"
if ($confirmation -and $confirmation.ToLower() -ne 's' -and $confirmation.ToLower() -ne 'y' -and $confirmation.ToLower() -ne 'yes' -and $confirmation.ToLower() -ne 'sim') {
    Write-Host "❌ Compilação cancelada pelo usuário" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "📦 Verificando e instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "🔨 COMPILANDO VERSÃO PREMIUM..." -ForegroundColor Cyan
Write-Host "   ⏳ Isso pode levar alguns minutos..."

$build_name = "tts_hotkey_premium"
$timestamp = Get-Date -Format "yyyyMMdd_HHmm"

pyinstaller --onefile `
    --hidden-import=requests `
    --hidden-import=urllib3 `
    --hidden-import=certifi `
    --hidden-import=keyboard `
    --hidden-import=pyttsx3 `
    --hidden-import=sounddevice `
    --hidden-import=soundfile `
    --hidden-import=pystray `
    --hidden-import=PIL `
    --hidden-import=numpy `
    --distpath=dist `
    --workpath=build `
    --name="$build_name" `
    --console `
    --icon=icon.png `
    --clean `
    $config_file

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" * 70
    Write-Host "🎉 COMPILAÇÃO CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
    Write-Host "=" * 70
    
    $exe_path = "dist/$build_name.exe"
    $exe_size = if (Test-Path $exe_path) { 
        [math]::Round((Get-Item $exe_path).Length / 1MB, 1) 
    } else { 
        "?" 
    }
    
    Write-Host ""
    Write-Host "📁 ARQUIVO GERADO:" -ForegroundColor Cyan
    Write-Host "   Localização: $exe_path" -ForegroundColor White
    Write-Host "   Tamanho: $exe_size MB" -ForegroundColor White
    Write-Host "   Compilado: $(Get-Date -Format 'dd/MM/yyyy HH:mm')" -ForegroundColor White
    
    Write-Host ""
    Write-Host "🎯 CARACTERÍSTICAS DA VERSÃO PREMIUM:" -ForegroundColor Cyan
    Write-Host "   ✅ Configuração completamente embutida"
    Write-Host "   ✅ Zero dependências externas"
    Write-Host "   ✅ Triggers personalizados"
    Write-Host "   ✅ Interface profissional"
    Write-Host "   ✅ Logs detalhados configuráveis"
    Write-Host "   ✅ Pronto para distribuição"
    
    Write-Host ""
    Write-Host "🚀 COMO USAR:" -ForegroundColor Yellow
    Write-Host "   1. Execute: $exe_path"
    Write-Host "   2. Use os triggers configurados para falar"
    Write-Host "   3. Enjoy! 🎉"
    
    Write-Host ""
    Write-Host "🔧 PARA RECONFIGURAR:" -ForegroundColor Magenta
    Write-Host "   1. Edite a classe Config em: $config_file"
    Write-Host "   2. Execute este script novamente"
    Write-Host "   3. Novo .exe será gerado com suas configurações"
    
    Write-Host ""
    Write-Host "=" * 70
    
} else {
    Write-Host ""
    Write-Host "=" * 70
    Write-Host "❌ ERRO NA COMPILAÇÃO!" -ForegroundColor Red
    Write-Host "=" * 70
    Write-Host ""
    Write-Host "🔍 POSSÍVEIS CAUSAS:"
    Write-Host "   - Dependências não instaladas corretamente"
    Write-Host "   - Erro de sintaxe no arquivo de configuração"
    Write-Host "   - PyInstaller não instalado (pip install pyinstaller)"
    Write-Host ""
    Write-Host "💡 SOLUÇÕES:"
    Write-Host "   1. Verifique o arquivo: $config_file"
    Write-Host "   2. Execute: pip install -r requirements.txt"
    Write-Host "   3. Execute: pip install pyinstaller"
    Write-Host "   4. Tente novamente"
}

Write-Host ""
Read-Host "Pressione Enter para finalizar"