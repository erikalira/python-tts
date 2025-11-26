# Sistema de Timeout Inteligente para Voz

## 🎯 Objetivo
Resolver o erro `WebSocket closed with 4006` mantendo o bot conectado para múltiplos comandos seguidos, mas desconectando automaticamente após inatividade.

## 🔧 Como Funciona

### Comportamento Atual:
1. **Primeiro comando `/speak`**:
   - Bot conecta ao canal de voz
   - Reproduz o áudio
   - **Agenda desconexão automática em 3 minutos**

2. **Comando seguinte dentro de 3 minutos**:
   - Bot já está conectado (não precisa reconectar)
   - **Cancela** a desconexão agendada
   - Reproduz o áudio
   - **Reagenda** nova desconexão para +3 minutos

3. **Sem atividade por 3 minutos**:
   - Bot desconecta automaticamente
   - Libera recursos do servidor
   - Evita erro 4006

### Vantagens:
✅ **Performance**: Comandos seguidos são instantâneos (sem latência de reconexão)  
✅ **Estabilidade**: Desconecta antes do Discord invalidar a sessão (erro 4006)  
✅ **Economia**: Libera recursos quando não está em uso (importante no plano free do Render)  
✅ **Transparente**: Usuário não percebe a diferença

## ⚙️ Configuração

O timeout está configurado em `src/infrastructure/discord/voice_channel.py`:

```python
IDLE_DISCONNECT_TIMEOUT = 180  # 3 minutos em segundos
```

### Ajustar o Timeout:
- **Uso frequente** (servidor ativo): aumentar para 300s (5 min) ou 600s (10 min)
- **Economia máxima** (baixo uso): reduzir para 60s (1 min) ou 120s (2 min)
- **Recomendado**: manter em 180s (3 min) - equilíbrio perfeito

## 📊 Logs

O sistema adiciona logs informativos:

```
INFO:src.infrastructure.discord.voice_channel:[VOICE_CHANNEL] Scheduling auto-disconnect in 180s
INFO:src.infrastructure.discord.voice_channel:[VOICE_CHANNEL] Cancelling scheduled disconnect (new activity)
INFO:src.infrastructure.discord.voice_channel:[VOICE_CHANNEL] Auto-disconnecting after 180s of inactivity
INFO:src.infrastructure.discord.voice_channel:[VOICE_CHANNEL] Auto-disconnect completed
```

## 🧪 Testando

1. **Teste de reconexão rápida**:
   ```
   /speak Teste 1
   # Espere 5 segundos
   /speak Teste 2  ← Deve ser instantâneo (já conectado)
   ```

2. **Teste de timeout**:
   ```
   /speak Teste
   # Espere 3 minutos
   # Bot deve desconectar automaticamente
   # Logs devem mostrar "Auto-disconnect completed"
   ```

3. **Teste de cancelamento**:
   ```
   /speak Teste 1
   # Espere 2 minutos (quase timeout)
   /speak Teste 2  ← Timer é resetado, bot continua conectado
   ```

## 🐛 Troubleshooting

**Bot desconecta muito rápido?**
- Aumentar `IDLE_DISCONNECT_TIMEOUT` para 300 ou 600 segundos

**Ainda recebendo erro 4006?**
- Verificar logs: o timeout está sendo executado?
- Reduzir timeout para forçar desconexão mais rápida
- Verificar se há múltiplas instâncias rodando

**Bot não desconecta automaticamente?**
- Verificar logs: procurar por "Scheduling auto-disconnect"
- Pode haver erro silencioso - verificar stack trace nos logs

## 📝 Implementação Técnica

A implementação usa `asyncio.Task` para agendar desconexões assíncronas:

```python
# Após reproduzir áudio
self._schedule_disconnect()  # Cria Task com sleep(180)

# Se novo comando chegar
self._cancel_disconnect_timer()  # Cancela Task anterior
# ... reproduz novo áudio ...
self._schedule_disconnect()  # Cria nova Task
```

Isso é thread-safe e não bloqueia o event loop do Discord.
