# 🎤 TTS Hotkey Premium - Configuração Avançada

## 🏆 Versão Premium: Configuração Inteligente

**Arquivo**: `tts_hotkey_configurable.py` → `tts_hotkey_premium.exe`

### ✨ **Discord ID Automático**

A versão premium pode encontrar automaticamente em qual canal você está!

```python
class Config:
    # 🌐 Discord Configuration
    DISCORD_BOT_URL = "https://python-tts-s3z8.onrender.com"
    DISCORD_MEMBER_ID = "123456789012345678"  # Seu Discord ID
    DISCORD_CHANNEL_ID = None  # Opcional
```

## 🔧 **Como Descobrir seu Discord ID**

### Passo 1: Ativar Modo Desenvolvedor
1. Discord → **Configurações do Usuário**
2. **Avançado** → Ativar **Modo Desenvolvedor**

### Passo 2: Copiar seu ID
1. Clique direito no **seu nome** em qualquer chat
2. **Copiar ID do Usuário**
3. Cole na Config class

## 🎯 **Funcionamento Inteligente**

O bot usa esta **ordem de prioridade**:

1. 🎯 **Canal já conectado** (se usou `/join` antes)
2. 📍 **Channel ID específico** (se configurou `DISCORD_CHANNEL_ID`)  
3. 👤 **Member ID** (encontra onde você está)
4. ❌ **Erro** se nenhuma opção funcionar

## 🎮 **Configurações por Perfil**

### Gaming Profile (Resposta Rápida)
```python
class Config:
    DISCORD_BOT_URL = "https://python-tts-s3z8.onrender.com"
    DISCORD_MEMBER_ID = "seu_id_aqui"
    TTS_RATE = 200                    # Fala rápida
    SHOW_NOTIFICATIONS = False        # Sem distrações
    REQUEST_TIMEOUT = 5               # Timeout baixo
```

### Office Profile (Mais Confiável)  
```python
class Config:
    DISCORD_BOT_URL = "https://python-tts-s3z8.onrender.com"
    DISCORD_MEMBER_ID = "seu_id_aqui" 
    TTS_RATE = 150                    # Fala clara
    SHOW_NOTIFICATIONS = True         # Feedback visual
    REQUEST_TIMEOUT = 15              # Mais tolerante
```

### Streaming Profile (OBS Ready)
```python
class Config:
    DISCORD_BOT_URL = "https://python-tts-s3z8.onrender.com"
    DISCORD_CHANNEL_ID = "id_do_canal_fixo"  # Canal específico
    TTS_RATE = 160                           # Boa para stream
    CONSOLE_LOGS = False                     # Sem logs no OBS
    SHOW_NOTIFICATIONS = False               # UI limpa
```

## ⚡ **Triggers Personalizáveis**

Evite conflitos com outros programas:

```python
class Config:
    # Triggers únicos para cada cenário
    TRIGGER_OPEN = "["        # Gaming: não conflita com chat
    TRIGGER_CLOSE = "]"       # Gaming: fácil de digitar
    
    # OU para Office:
    TRIGGER_OPEN = "="        # Office: tecla única
    TRIGGER_CLOSE = "+"       # Office: ao lado no teclado
```

## 🔊 **Configuração de Áudio Avançada**

```python
class Config:
    # Dispositivo de áudio específico (opcional)
    AUDIO_DEVICE = None              # Padrão do sistema
    # AUDIO_DEVICE = "VB-Cable"     # Para streaming
    # AUDIO_DEVICE = "Headset"      # Para gaming
    
    # Configurações de TTS
    TTS_RATE = 180                   # Velocidade (120-300)
    TTS_VOLUME = 0.9                 # Volume (0.0-1.0)  
    TTS_LANGUAGE = "pt"              # Idioma
```

## 📊 **Dashboard de Status Premium**

Quando executado, mostra status completo:

```
================================================================
🎯 TTS Hotkey Premium - Configuration Dashboard
================================================================
🌐 Discord: ✅ https://python-tts-s3z8.onrender.com
👤 Member ID: ✅ 123456789012345678
🎤 TTS Engine: ✅ Portuguese, Rate: 180
⌨️ Triggers: ✅ { } - No conflicts detected
🔊 Audio: ✅ Default output device
⚡ Network: ✅ Timeout: 10s
================================================================
```

## 🚀 **Compilar e Usar**

```powershell
# 1. Configurar
code tts_hotkey_configurable.py

# 2. Compilar
./build_configurable.ps1

# 3. Usar
dist/tts_hotkey_premium.exe
```

## 🎯 **Modo de Uso**

1. **Entre em um canal de voz** no Discord
2. **Execute o .exe** (dashboard aparece)
3. **Aperte sua trigger key** (ex: `{`)
4. **Digite o texto** que quer falar
5. **Aperte a close key** (ex: `}`)
6. **Bot fala automaticamente!**

## 🛠️ **Troubleshooting Premium**

### ❌ "Hotkey registration failed"
```python
# Mude os triggers:
TRIGGER_OPEN = "["
TRIGGER_CLOSE = "]" 
```

### ❌ "Discord not found"
```python
# Verifique a URL:
DISCORD_BOT_URL = "https://python-tts-s3z8.onrender.com"
```

### ❌ "Member not found"
```python  
# Use o ID correto ou configure canal fixo:
DISCORD_CHANNEL_ID = "987654321098765432"
```

## 💎 **Vantagens da Versão Premium**

- 🎯 **Zero arquivos externos** - tudo embutido
- 🎮 **Perfis especializados** pré-configurados
- 📊 **Dashboard visual** com status detalhado
- ⚡ **Build inteligente** detecta problemas
- 🔧 **Altamente configurável** sem hardcode
- 🎨 **Interface profissional** com logs coloridos

**Resultado**: Um único arquivo `.exe` totalmente personalizado para suas necessidades!