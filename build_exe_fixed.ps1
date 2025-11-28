# Instalar dependências
pip install -r requirements.txt

# Compilar com todas as dependências necessárias
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
    --add-data=".env;." `
    --add-data="icon.png;." `
    --name=tts_hotkey_fixed `
    --console `
    src/tts_hotkey.py

# Copiar arquivos necessários para o diretório de saída
Copy-Item ".env" "dist/.env" -ErrorAction SilentlyContinue
Copy-Item "icon.png" "dist/icon.png" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=================================="
Write-Host "✅ Executável criado com sucesso!"
Write-Host "=================================="
Write-Host "Localização: dist/tts_hotkey_fixed.exe"
Write-Host ""
Write-Host "INSTRUÇÕES IMPORTANTES:"
Write-Host "1. Certifique-se de que o arquivo .env está no mesmo diretório do .exe"
Write-Host "2. Execute o .exe em um prompt de comando para ver os logs de debug"
Write-Host "3. Se ainda não funcionar, defina as variáveis de ambiente do sistema:"
Write-Host "   set DISCORD_BOT_URL=https://python-tts-s3z8.onrender.com"
Write-Host ""
Write-Host "Para testar a conexão primeiro, execute:"
Write-Host "   python test_discord_connection.py"
Write-Host "=================================="