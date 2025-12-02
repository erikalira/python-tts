# Script de compilação standalone - SEM necessidade de .env externo!

Write-Host ""
Write-Host "=================================="
Write-Host "🚀 COMPILANDO TTS HOTKEY STANDALONE"
Write-Host "=================================="
Write-Host ""

# Instalar dependências
Write-Host "📦 Instalando dependências..."
pip install -r requirements.txt

Write-Host ""
Write-Host "🔨 Compilando executável standalone..."

# Compilar com todas as dependências, SEM precisar de .env externo
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
    --hidden-import=python_dotenv `
    --hidden-import=numpy `
    --name=tts_hotkey_standalone `
    --console `
    --icon=icon.png `
    src/tts_hotkey.py

Write-Host ""
Write-Host "=================================="
Write-Host "✅ EXECUTÁVEL STANDALONE CRIADO!"
Write-Host "=================================="
Write-Host "Localização: dist/tts_hotkey_standalone.exe"
Write-Host ""
Write-Host "🎉 VANTAGENS:"
Write-Host "   ✅ Não precisa de arquivo .env separado"
Write-Host "   ✅ Configuração embutida no executável"
Write-Host "   ✅ Funciona em qualquer máquina Windows"
Write-Host "   ✅ Só um arquivo .exe para distribuir"
Write-Host ""
Write-Host "📝 PARA PERSONALIZAR:"
Write-Host "   - Edite as configurações em src/tts_hotkey.py"
Write-Host "   - Recompile com este script"
Write-Host ""
Write-Host "🚀 PARA USAR:"
Write-Host "   - Execute: dist/tts_hotkey_standalone.exe"
Write-Host "   - Digite {texto} em qualquer lugar"
Write-Host "=================================="