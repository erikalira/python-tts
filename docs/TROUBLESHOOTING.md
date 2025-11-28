# 🎯 TTS Hotkey Premium - Guia de Resolução

## ✅ Versão Premium: Zero Problemas de Configuração!

**Arquivo**: `tts_hotkey_premium.exe` (gerado de `tts_hotkey_configurable.py`)

### 🚀 **Por que a versão Premium não tem estes problemas?**

- 🎯 **Sem arquivos externos** - tudo embutido no executável
- 🔧 **Configuração centralizada** - editável antes da compilação
- 💎 **Build inteligente** - detecta problemas automaticamente
- 📊 **Logs avançados** - mostra exatamente o que está acontecendo

### 🔍 **Diagnóstico Rápido**

Execute `tts_hotkey_premium.exe` e observe a **tela colorida de status**:

```
🎯 TTS Hotkey Premium v2.0 - Configuração Centralizada
================================================================
✅ Discord URL: https://python-tts-s3z8.onrender.com
✅ TTS Engine: Configurado (Rate: 180)
✅ Triggers: { para iniciar, } para falar
✅ Hotkeys: Registrados com sucesso
================================================================
```

## 🛠️ **Problemas Raros e Soluções**

### 1. ❌ "Failed to register hotkey"

**Causa**: Outro programa já está usando suas teclas configuradas.

**Solução**:

```python
# Em tts_hotkey_configurable.py, mude os triggers:
class Config:
    TRIGGER_OPEN = "["     # Em vez de "{"
    TRIGGER_CLOSE = "]"    # Em vez de "}"
```

### 2. ❌ "Discord connection failed"

**Causa**: URL do bot incorreto ou bot offline.

**Solução**:

```python
# Verifique a URL em tts_hotkey_configurable.py:
class Config:
    DISCORD_BOT_URL = "https://python-tts-s3z8.onrender.com"  # URL correta?
```

### 3. ❌ "TTS engine failed"

**Causa**: Sistema de TTS não disponível.

**Solução**:

```python
# Ajuste as configurações de TTS:
class Config:
    TTS_RATE = 150         # Reduza a velocidade
    TTS_LANGUAGE = "pt"    # Confirme o idioma
```

### 4. ⚠️ "Network timeout"

**Causa**: Conexão lenta ou instável.

**Solução**:

```python
# Aumente o timeout:
class Config:
    REQUEST_TIMEOUT = 30   # 30 segundos em vez de 10
```

## 🔧 **Build Script Inteligente**

O `build_configurable.ps1` detecta automaticamente problemas:

```powershell
# Execute para ver análise completa:
./build_configurable.ps1
```

**Output esperado**:

```
🔍 Analisando configuração...
✅ Discord URL: Valid
✅ Triggers: Sem conflitos
✅ TTS Config: OK
✅ Dependencies: All found
🚀 Building premium version...
```

## 📊 **Dashboard de Status**

A versão premium inclui dashboard visual quando executada:

```
================================================================
🎯 TTS Hotkey Premium - Status Dashboard
================================================================
🌐 Discord: ✅ Connected (python-tts-s3z8.onrender.com)
🎤 TTS: ✅ Ready (Portuguese, Rate: 180)
⌨️ Hotkeys: ✅ { } registered successfully
🔊 Audio: ✅ Default output device detected
💾 Config: ✅ All settings validated
================================================================
```

## 🎮 **Perfis Especializados**

Se tiver problemas, teste outros perfis incluídos:

```python
# Gaming Profile (menos recursos, mais estável)
class Config:
    TTS_RATE = 200
    SHOW_NOTIFICATIONS = False
    CONSOLE_LOGS = False

# Office Profile (mais tolerante a erros)
class Config:
    REQUEST_TIMEOUT = 30
    TTS_RATE = 150
    CONSOLE_LOGS = True
```

## ⚡ **Recompilar Rapidamente**

```powershell
# 1. Ajuste a classe Config
code tts_hotkey_configurable.py

# 2. Compile novamente
./build_configurable.ps1

# 3. Teste imediatamente
dist/tts_hotkey_premium.exe
```

## 🆘 **Se Nada Funcionar**

1. **Teste a configuração** antes de compilar:

```python
python3 -c "from tts_hotkey_configurable import Config; print('Config OK!')"
```

2. **Verifique dependências**:

```powershell
pip install -r requirements.txt
```

3. **Build limpo**:

```powershell
Remove-Item dist, build -Recurse -Force -ErrorAction SilentlyContinue
./build_configurable.ps1
```

**🎯 Resultado**: Um único arquivo robusto sem dependências externas!
