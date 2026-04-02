# 🎯 TTS Hotkey - Guia de Resolução

## ✅ Desktop App Atual

**Entry point**: `app.py`  
**Executável de build**: `dist/tts_hotkey_clean.exe`

### 🔍 Diagnóstico Rápido

Execute `python app.py` durante o desenvolvimento ou `dist/tts_hotkey_clean.exe` após o build
e observe os logs de inicialização do Desktop App.

## 🛠️ **Problemas Raros e Soluções**

### 1. ❌ "Failed to register hotkey"

**Causa**: Outro programa já está usando suas teclas configuradas.

**Solução**:

Abra a configuração do Desktop App e troque as hotkeys para outra combinação sem conflito.

### 2. ❌ "Discord connection failed"

**Causa**: URL do bot incorreto ou bot offline.

**Solução**:

Verifique `DISCORD_BOT_URL` no `.env` ou na configuração persistida do Desktop App.

### 3. ❌ "TTS engine failed"

**Causa**: Sistema de TTS não disponível.

**Solução**:

Abra a interface de configuração do app e ajuste engine, idioma ou taxa de fala.

### 4. ⚠️ "Network timeout"

**Causa**: Conexão lenta ou instável.

**Solução**:

Se necessário, aumente o timeout na configuração persistida do Desktop App.

## 🔧 **Build Script Inteligente**

O `scripts/build/build_clean_architecture.ps1` empacota o runtime atual:

```powershell
# Execute para gerar o .exe:
./scripts/build/build_clean_architecture.ps1
```

## ⚡ **Recompilar Rapidamente**

```powershell
# 1. Ajuste dependências/configuração se necessário
code app.py

# 2. Compile novamente
./scripts/build/build_clean_architecture.ps1

# 3. Teste imediatamente
dist/tts_hotkey_clean.exe
```

## 🆘 **Se Nada Funcionar**

1. **Verifique dependências**:

```powershell
pip install -r requirements.txt
```

2. **Build limpo**:

```powershell
Remove-Item dist, build -Recurse -Force -ErrorAction SilentlyContinue
./scripts/build/build_clean_architecture.ps1
```

3. **Teste o entrypoint atual**:

```powershell
python app.py
```

**🎯 Resultado**: um único runtime do Desktop App com Clean Architecture, sem wrapper legado.
