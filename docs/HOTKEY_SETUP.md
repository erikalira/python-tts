# 🎤 TTS Hotkey - Configuração Avançada

## 🏆 Desktop App Atual

**Entry point**: `app.py`  
**Executável**: `dist/tts_hotkey_clean.exe`

### ✨ Discord ID Automático

O Desktop App usa a configuração persistida para descobrir em qual canal você está.

## 🔧 **Como Descobrir seu Discord ID**

### Passo 1: Ativar Modo Desenvolvedor

1. Discord → **Configurações do Usuário**
2. **Avançado** → Ativar **Modo Desenvolvedor**

### Passo 2: Copiar seu ID

1. Clique direito no **seu nome** em qualquer chat
2. **Copiar ID do Usuário**
3. Cole na interface de configuração do app

## 🎯 **Funcionamento Inteligente**

O bot usa esta **ordem de prioridade**:

1. 🎯 **Canal já conectado** (se usou `/join` antes)
2. 📍 **Channel ID específico** (se configurou `DISCORD_CHANNEL_ID`)
3. 👤 **Member ID** (encontra onde você está)
4. ❌ **Erro** se nenhuma opção funcionar

## 🎮 **Configurações por Perfil**

### Perfis sugeridos

- Gaming: taxa de fala mais alta e menos notificações
- Office: taxa mais baixa e timeout maior
- Streaming: canal fixo e menos logs visuais

## ⚡ **Triggers Personalizáveis**

Evite conflitos com outros programas:

Escolha uma combinação de abertura/fechamento que não conflite com outros programas.

## 🔊 **Configuração de Áudio Avançada**

Configure engine, idioma, taxa e dispositivo de áudio pela interface do Desktop App.

## 📊 Status

Quando executado, o app mostra logs de inicialização e status dos serviços do Desktop App.

## 🚀 **Compilar e Usar**

```powershell
# 1. Rodar o app
python app.py

# 2. Compilar
./scripts/build/build_clean_architecture.ps1

# 3. Usar
dist/tts_hotkey_clean.exe
```

## 🎯 **Modo de Uso**

1. **Entre em um canal de voz** no Discord
2. **Execute o app** (`python app.py` ou o `.exe`)
3. **Aperte sua trigger key** (ex: `{`)
4. **Digite o texto** que quer falar
5. **Aperte a close key** (ex: `}`)
6. **Bot fala automaticamente!**

## 🛠️ **Troubleshooting Premium**

### ❌ "Hotkey registration failed"

Mude as hotkeys na interface de configuração do app.

### ❌ "Discord not found"

Verifique a URL do bot na configuração do app ou no `.env`.

### ❌ "Member not found"

Use o ID correto do usuário ou configure um canal fixo na interface do app.

## 💎 Vantagens da Versão Atual

- 🎯 Um único runtime do Desktop App
- 📊 Configuração persistida
- ⚡ Build dedicado para Windows
- 🔧 Menos caminhos paralelos de execução

**Resultado**: um único `.exe` baseado no runtime limpo de `src/standalone`.
