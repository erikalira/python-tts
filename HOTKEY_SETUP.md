# 🎤 Configuração do Hotkey TTS

Este documento explica como configurar o script `tts_hotkey.py` para se comunicar com o bot Discord no Render.

## 🎯 Problema

Quando você usa `{texto}` no teclado, o script envia para o endpoint `/speak`, mas o bot não sabe **em qual canal de voz você está**. Por isso o erro:

```
[USE_CASE] Error during audio playback: Not connected to voice channel
```

## ✅ Solução 1: Usar canal já conectado (RECOMENDADO)

**Essa solução já foi implementada!** O bot agora:

1. **SEMPRE verifica primeiro** se ele já está conectado em algum canal
2. Se estiver, usa esse canal para tocar o áudio
3. Só tenta procurar por IDs se não estiver conectado

### Como usar:

1. Entre no Discord em um canal de voz
2. Use o comando `/join` no Discord para conectar o bot
3. Agora use o hotkey `{texto}` - o bot vai falar no canal onde ele já está! 🎉

**Vantagem:** Não precisa configurar nada no `.env`

## 🔧 Solução 2: Configurar seu Discord Member ID

Se você quer que o bot **encontre automaticamente** em qual canal você está (mesmo sem usar `/join` antes), adicione seu Discord ID ao `.env`:

### Passo 1: Descobrir seu Discord Member ID

1. Abra Discord
2. Vá em **Configurações do Usuário** > **Avançado**
3. Ative **Modo Desenvolvedor**
4. Clique com botão direito no seu nome
5. Clique em **Copiar ID do Usuário**

### Passo 2: Adicionar ao .env

Crie ou edite o arquivo `.env` na mesma pasta do `tts_hotkey.py`:

```env
# URL do bot no Render
DISCORD_BOT_URL=https://tts-hotkey-windows.onrender.com

# Seu Discord Member ID (copie do Discord com Modo Desenvolvedor ativado)
DISCORD_MEMBER_ID=123456789012345678

# Opcional: ID do canal específico (se quiser forçar um canal fixo)
# DISCORD_CHANNEL_ID=987654321098765432
```

### Passo 3: Testar

Agora quando você usar `{texto}`, o bot vai:

1. Procurar se você está conectado em algum canal de voz
2. Entrar nesse canal automaticamente
3. Tocar o áudio

## 🔄 Fluxo de Busca do Canal

O bot procura nessa ordem:

1. ✅ **Canal onde o bot JÁ está conectado** ← NOVA PRIORIDADE!
2. `channel_id` (se configurado no `.env` com `DISCORD_CHANNEL_ID`)
3. `member_id` (se configurado no `.env` com `DISCORD_MEMBER_ID`)
4. Qualquer canal disponível no servidor (fallback)

## 🐛 Troubleshooting

### Bot ainda não entra no canal

**Verifique se:**
- Você usou `/join` no Discord primeiro (Solução 1)
- OU configurou o `DISCORD_MEMBER_ID` corretamente (Solução 2)
- O bot tem permissões para entrar no canal
- Você reiniciou o `tts_hotkey.py` depois de editar o `.env`

### Erro "Not connected to voice channel"

**Isso acontece quando:**
- Você não usou `/join` E não configurou `DISCORD_MEMBER_ID`
- O bot não consegue encontrar em qual canal você está
- O Render está em cold start (primeira requisição falha, segunda funciona)

**Solução:** Use `/join` primeiro ou configure o `DISCORD_MEMBER_ID` no `.env`

## 📝 Exemplo de Uso Completo

### Opção A: Com /join (sem configuração)

```bash
# 1. Entre em um canal de voz no Discord
# 2. Digite no Discord: /join
# 3. Aperte {texto para falar}
# ✅ Bot fala no canal onde está conectado!
```

### Opção B: Com DISCORD_MEMBER_ID (automático)

```bash
# 1. Configure .env com seu DISCORD_MEMBER_ID
# 2. Entre em qualquer canal de voz no Discord
# 3. Aperte {texto para falar}
# ✅ Bot encontra você e entra no canal automaticamente!
```

## 🚀 Melhorias Implementadas

- ✅ Bot procura primeiro o canal onde JÁ está conectado
- ✅ Logs detalhados para debug
- ✅ Delays para garantir conexão antes de tocar áudio
- ✅ Fallback para TTS local se bot não responder
- ✅ Timeout de 10s para requisições HTTP

---

**Dica:** Use a Solução 1 (`/join` primeiro) se você sempre usa o mesmo canal. É mais simples! 😊
