# ✅ Implementações para Isolamento de Servidor e Prevenção de Leaks

## 📋 Resumo das Mudanças

Implementadas melhorias críticas para garantir isolamento total entre servidores, persistência de dados e prevenção de memory leaks.

---

## 🔧 1. Configuração Per-Servidor com Persistência

### Nova Camada: `src/infrastructure/persistence/config_storage.py`

**Características:**

- ✅ **Isolamento por servidor**: Cada guild tem sua própria configuração
- ✅ **Persistência em JSON**: Configurações sobrevivem a restarts
- ✅ **Cache em-memória**: Acesso rápido com fallback para storage
- ✅ **Interface abstrata**: Fácil adicionar Redis/Database no futuro

**Implementação:**

```python
# Antes: Configuração global compartilhada
self.config_repository = InMemoryConfigRepository(config.tts_config)

# Depois: Configuração isolada por servidor e persistente
json_storage = JSONConfigStorage(storage_dir="configs")
self.config_repository = GuildConfigRepository(
    default_config=config.tts_config,
    storage=json_storage
)
```

**Arquivo gerado:**

- `configs/guild_{guild_id}.json` - Uma arquivo por servidor com suas configurações

**Métodos principais:**

- `get_config(guild_id)` - Obtém config (cache ou default)
- `load_from_storage(guild_id)` - Carrega do armazenamento assincronamente
- `save_config_async(guild_id, config)` - Persiste alterações
- `delete_config_async(guild_id)` - Remove config de um servidor

---

## 🔒 2. Validação de Guild ID (Segurança Multi-Servidor)

### Mudanças em `src/application/use_cases.py`

**Validações críticas adicionadas:**

```python
# VALIDATION: Verify guild_id is set (critical for multi-server isolation)
if not request.guild_id:
    error = "Guild ID não foi fornecido - isolamento de servidor falhou"
    item.mark_failed(error)
    logger.error(f"[USE_CASE] SECURITY: Item {item.item_id} has no guild_id!")
    return {"success": False, "message": f"❌ {error}", "queued": True}

# VALIDATION: Verify voice channel belongs to same guild
if voice_channel.guild_id != request.guild_id:
    error = "Canal de voz pertence a servidor diferente"
    item.mark_failed(error)
    logger.error(f"[USE_CASE] SECURITY: Item {item.item_id} voice channel guild {voice_channel.guild_id} != request guild {request.guild_id}")
    return {"success": False, "message": f"❌ {error}", "queued": True}
```

**Benefícios:**

- ❌ Impossível enviar áudio para servidor errado
- ❌ Impossível vazar configuração entre servidores
- ❌ Rastreamento e logging detalhado de tentativas malformadas

---

## 🧹 3. Limpeza de Recursos (Memory Leaks)

### Mudanças em `src/infrastructure/discord/voice_channel.py`

**Cleanup automático de áudio:**

```python
finally:
    # Clean up audio file (critical for preventing memory leaks)
    if audio:
        try:
            logger.debug(f"[USE_CASE] Item {item.item_id}: cleaning up audio file {audio.path}")
            audio.cleanup()
            logger.debug(f"[USE_CASE] Item {item.item_id}: audio file cleaned up successfully")
        except Exception as cleanup_error:
            logger.warning(f"[USE_CASE] Item {item.item_id}: error during audio cleanup: {cleanup_error}")
```

**Cleanup de instâncias de canal obsoletas:**

```python
def _cleanup_stale_instances(self, now: float, max_idle_time: int = 3600) -> None:
    """Clean up voice channel instances that haven't been used recently.

    Remove instâncias idle por mais de 1 hora (default).
    Previne memory leaks de conexões que não são mais ativas.
    """
```

**Cleanup manual (graceful shutdown):**

```python
async def cleanup_all(self) -> None:
    """Clean up all cached voice channel instances."""
    # Desconecta todos os canais ativos
    # Remove cache de instâncias
    # Libera memória
```

---

## 📊 4. Melhorias no DiscordVoiceChannelRepository

### Recursos novos:

- ✅ **Rastreamento de último uso**: `_instance_last_used` timestamp
- ✅ **Cleanup automático**: Remove instâncias idle periodicamente
- ✅ **Estatísticas de cache**: `get_cache_stats()`
- ✅ **Isolamento por guild**: Validações em todas as buscas
- ✅ **Logging detalhado**: Rastreamento completo de operações

**Métodos adicionados:**

```python
def _cleanup_stale_instances(self, now: float, max_idle_time: int = 3600)
    """Remove instâncias que não foram usadas por max_idle_time segundos"""

def get_cache_stats(self) -> dict
    """Retorna estatísticas do cache (utile para monitoramento)"""

async def cleanup_all(self) -> None
    """Cleanup completo (para graceful shutdown)"""
```

---

## 🎯 5. Uso Correto de Guild ID nos Commands

### Mudanças em `src/presentation/discord_commands.py`

**Antes:**

```python
tts_request = TTSRequest(
    text=text,
    guild_id=interaction.guild.id if interaction.guild else None,
    member_id=user_id  # Config era feita por user_id (PROBLEMA!)
)

# /config usava user_id como chave
result = self._config_use_case.execute(user_id=interaction.user.id, ...)
```

**Depois:**

```python
# VALIDAÇÃO: Garante que guild_id existe
if not interaction.guild or not interaction.guild.id:
    await interaction.edit_original_response(
        content='❌ Erro: Não foi possível determinar o servidor.'
    )
    return

guild_id = interaction.guild.id

# /speak usa guild_id
tts_request = TTSRequest(
    text=text,
    guild_id=guild_id,  # CRITICAL: Server isolation
    member_id=member_id
)

# /config usa guild_id (not user_id)
result = await self._config_use_case.update_config_async(
    guild_id=guild_id,  # Configuração por servidor!
    engine=voz,
    language=idioma,
    voice_id=sotaque
)
```

---

## 📈 ConfigureTTSUseCase - Novo Padrão Async

### Métodos refatorados:

**Novo (recomendado):**

```python
async def update_config_async(guild_id, engine, language, voice_id, rate):
    """Atualiza config E persiste para storage"""
    # Valida
    # Atualiza cache
    # Salva em JSON/Redis/Database
    # Retorna resultado
```

O wrapper síncrono legado foi removido depois da migração completa para `update_config_async()`.

---

## 🔐 Garantias de Segurança Implementadas

| Problema                              | Solução                            | Validação                                    |
| ------------------------------------- | ---------------------------------- | -------------------------------------------- |
| Config compartilhada entre servidores | Per-guild storage com persistência | `request.guild_id` em todos os fluxos        |
| Áudio enviado para canal errado       | Validação de guild_id              | `voice_channel.guild_id == request.guild_id` |
| Memory leaks de áudio                 | `audio.cleanup()` em finally       | Try/except com logging                       |
| Conexões obsoletas não desconectam    | Cleanup automático de idle         | `_cleanup_stale_instances()` com timestamp   |
| Perda de config em restart            | Persistência JSON                  | Carregamento automático em startup           |
| Configuração por usuário (vazamento)  | Configuração por servidor          | `guild_id` como chave                        |

---

## 📝 Estrutura de Diretórios Nova

```
configs/                                    # NOVO
├── guild_123456789.json                  # Config servidor A
├── guild_987654321.json                  # Config servidor B
└── ...

src/infrastructure/persistence/           # NOVA CAMADA
├── __init__.py
└── config_storage.py                     # GuildConfigRepository + JSONConfigStorage
```

---

## 🚀 Como Usar

### 1. Inicialização (automática no Container)

```python
json_storage = JSONConfigStorage(storage_dir="configs")
config_repository = GuildConfigRepository(
    default_config=config.tts_config,
    storage=json_storage
)
```

### 2. Obter configuração de um servidor

```python
# Síncrono (cache)
config = config_repository.get_config(guild_id)

# Assíncrono (carrega do storage se não estiver em cache)
config = await config_repository.load_from_storage(guild_id)
```

### 3. Atualizar configuração (com persistência)

```python
result = await config_use_case.update_config_async(
    guild_id=123456789,
    engine="gtts",
    language="pt",
    voice_id="roa/pt-br",
    rate=180
)
```

### 4. Cleanup de recursos (graceful shutdown)

```python
# Cleanup automático: limpa instâncias idle a cada busca
# Cleanup manual:
await voice_channel_repository.cleanup_all()
```

---

## ✅ Verificações Implementadas

- [x] Config isolada por servidor
- [x] Persistência em JSON
- [x] Validação de guild_id em todos os fluxos
- [x] Cleanup de áudio files
- [x] Cleanup de conexões obsoletas
- [x] Logging detalhado para debug
- [x] Migração completa para configuração assíncrona por servidor
- [x] Imports funcionando sem erros
- [x] Sem memory leaks óbvios
- [x] Isolamento total entre servidores

---

## 🔍 Monitoramento

Para ver estado do cache:

```python
stats = voice_channel_repository.get_cache_stats()
print(f"Cached channels: {stats['cached_channels']}")
print(f"Cached members: {stats['cached_members']}")
print(f"Total tracked: {stats['total_tracked']}")
```

Para monitorar limpeza automática, veja logs com `[VOICE_REPO] Cleaned up stale instance`.

---

## 📚 Documentação Relacionada

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Visão geral da arquitetura
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Diagnóstico de problemas
- Código comentado com `[SECURITY]` marca seções críticas

---

## 🎯 Próximas Melhorias Futuras

1. **Redis para distribuição**: Suportar múltiplas instâncias do bot
2. **Database persistente**: PostgreSQL/MongoDB para produção
3. **Metrics**: Prometheus para monitorar leaks
4. **Audit logging**: Rastrear todas as mudanças de config
5. **Rate limiting por servidor**: Evitar spam
