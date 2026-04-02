# Discord Rate Limit (429) - Solução

## Problema

Seu bot está recebendo o erro `429 Too Many Requests` ao tentar conectar no Discord. Isso ocorre quando múltiplas tentativas de login são feitas em sequência rápida.

### Causas Comuns

1. **Token inválido ou expirado** - A aplicação foi deletada ou o token foi revogado
2. **Múltiplos redeploys rápidos** - O UptimeRobot faz checks frequentes causando redeploys sucessivos
3. **Múltiplas instâncias** - Mais de uma instância do bot tentando logar simultaneamente
4. **Falta de retry logic** - O bot falha imediatamente sem tentar novamente

## Soluções Implementadas ✅

### 1. Retry com Exponential Backoff

O runtime do bot foi atualizado com a função `start_discord_bot_with_retry()`:

```python
# Retry automático com backoff exponencial
# 1º tentativa: imediato
# 2º tentativa: 1 segundo
# 3º tentativa: 2 segundos
# 4º tentativa: 4 segundos
# 5º tentativa: 8 segundos
```

**Status**: ✅ Implementado

### 2. Health Check Endpoint

O servidor HTTP do bot já possui um endpoint `/health` que:

- Responde `200 OK` mesmo que o Discord bot esteja down
- Permite monitoramento independente da API

**Status**: ✅ Pronto para usar

## O que Fazer Agora

### Passo 1: Pausar o UptimeRobot Temporariamente ⚠️

O UptimeRobot está causando redeploys frequentes (a cada 5 minutos). Isso piora o rate limiting.

**Opções:**

- **Opção A** (Recomendado): Pause o monitoramento por 24-48 horas
  - Vá para https://dashboard.uptimerobot.com
  - Clique no monitor "python-tts-s3z8.onrender.com"
  - Clique em **Pause**
  - Aguarde o rate limit passar (Discord reseta a cada 1 hora aprox)

- **Opção B**: Aumente o intervalo para 30 minutos
  - Clique em **Edit** no monitor
  - Mude "Check interval" de 5 minutos para 30 minutos
  - Salve

### Passo 2: Aguardar Rate Limit Passar ⏱️

Discord reseta rate limits a cada ~1 hora. Após pausar o UptimeRobot:

1. Aguarde 10-15 minutos
2. Faça um novo deploy no Render (force redeploy)
3. Se ainda houver erro, aguarde mais 30 minutos e tente novamente

### Passo 3: Confirmar Token Válido ✅

Certifique-se de que:

1. **A aplicação existe no Discord Developer Portal**
   - Vá para https://discord.com/developers/applications
   - Procure pela sua aplicação
   - Se não encontrar, crie uma nova

2. **O token está correto**
   - Clique na aplicação
   - Vá em **Bot** → **Reset Token** → **Copy**
   - Compare com a variável `DISCORD_TOKEN` no Render

3. **O bot está no seu servidor**
   - Vá para **OAuth2 → URL Generator**
   - Marque: `bot` + `applications.commands` (Scopes)
   - Marque: `Send Messages`, `Use Slash Commands`, `Connect`, `Speak` (Permissions)
   - Copie a URL gerada
   - Abra em navegador e autorize

### Passo 4: Configurar UptimeRobot Corretamente

Após o rate limit passar e o bot estar online:

**Configure para monitorar o health endpoint (não a página principal):**

1. Abra o monitor do UptimeRobot
2. Mude a URL para: `https://python-tts-s3z8.onrender.com/health`
3. Aumente o intervalo para **30 minutos** (evita rate limit)
4. Salve e reative o monitor

**Por que `/health`?**

- Responde mesmo que o Discord bot esteja offline
- Não causa redeploys desnecessários
- Ainda garante que a API HTTP do bot está rodando

## Código Alterado

**Arquivo atual: `src/bot.py`**

Adicionada função `start_discord_bot_with_retry()` que:

- ✅ Detecta erros 429
- ✅ Espera com backoff exponencial
- ✅ Tenta até 5 vezes antes de falhar
- ✅ Log detalhado de cada tentativa

## Próximas Ações

1. ⏸️ **AGORA**: Pause o UptimeRobot (24-48 horas)
2. ⏳ **Aguarde**: 10-15 minutos
3. 🔄 **Deploy**: Faça um novo deploy no Render
4. ✅ **Teste**: Vá para https://python-tts-s3z8.onrender.com/health
5. 🎯 **Configure**: Reconfigure UptimeRobot com `/health` e intervalo 30m

## Troubleshooting

### Ainda recebendo 429 após 24 horas?

1. **Token pode estar inválido** - Gere um novo no Developer Portal
2. **Verifique a aplicação** - Confirme que existe no Discord
3. **Limite de requisições** - Discord pode ter limites por aplicação
4. **Tente esperar mais** - Às vezes leva 24-48 horas para reset total

### Como verificar se está funcionando?

```bash
# Acesse a API
curl https://python-tts-s3z8.onrender.com/health
# Resposta esperada: {"status": "healthy"}

curl https://python-tts-s3z8.onrender.com/version
# Resposta com versão e informações do bot
```

### O bot conecta mas não responde aos comandos?

- Verifique permissões do bot (Connect, Speak, Send Messages)
- Certifique-se de que o bot foi adicionado ao servidor
- Teste com `/join` e depois `/speak "test"`

## Referências

- [Discord Rate Limits](https://discord.com/developers/docs/topics/rate-limits)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [UptimeRobot Documentation](https://uptimerobot.com/help/)

---

**Ultima atualização**: 27/01/2026
**Status**: Soluções implementadas e documentadas ✅
