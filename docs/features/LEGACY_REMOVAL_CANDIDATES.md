# Legacy Removal Candidates

Este documento registra o legado remanescente após a migração para a estrutura em `src/` e ajuda a separar:

- o que já parece seguro remover
- o que ainda existe por compatibilidade
- quais documentos precisam refletir essa transição

## Contexto atual

Hoje o repositório mantém dois fluxos independentes:

- Desktop App Windows: entry point em `app.py`, implementação em `src/standalone/`
- Bot Discord: entry point oficial em `src/bot.py`

O runtime modular do bot usa `src/bot.py` com servidor HTTP em `src/infrastructure/http/server.py`.

## Removidos nesta limpeza

### 1. Referência documental a `src.test_server`

Status:
Removida da documentação operacional.

### 2. Método `_process_queue()` em `src/application/use_cases.py`

Status:
Removido.

Motivo:
O fluxo atual usa apenas o processamento de fila novo.

### 3. `src/app.py`

Status:
Removido.

Motivo:
Os endpoints operacionais do bot foram migrados para `src/infrastructure/http/server.py`.

Impacto:
O runtime do bot agora usa apenas `aiohttp` no caminho oficial.

### 4. Wrapper síncrono `ConfigureTTSUseCase.execute()`

Status:
Removido.

Motivo:
Os testes e o fluxo ativo foram migrados para `update_config_async()`.

### 5. Acoplamento de `application` com `infrastructure` para configuração

Status:
Removido.

Motivo:
Os use cases agora dependem de métodos assíncronos expostos no contrato de repositório, sem `isinstance(...)` nem import de implementação concreta.

### 6. Compatibilidade `voice_channel.guild_id`

Status:
Removida do código ativo.

Motivo:
A checagem de guild agora usa `get_guild_id()` no contrato de `IVoiceChannel`, evitando dependência implícita de atributo concreto.

## Documentação alinhada nesta rodada

Os ajustes feitos nesta rodada foram:

- remoção da referência a `src.test_server`
- promoção de `src/bot.py` a entry point oficial do bot
- remoção de `main.py` da documentação principal
- migração dos endpoints utilitários do bot para `src/infrastructure/http/server.py`
- remoção de `src/app.py`
- remoção do wrapper síncrono `ConfigureTTSUseCase.execute()`
- remoção de `_process_queue()`
- remoção do fallback `FLASK_PORT`
- remoção do acesso compatível `voice_channel.guild_id`
- remoção do acoplamento de `application` com implementações concretas de config
- adição deste inventário no índice de `docs/README.md`

## Próximo passo recomendado

Ordem mais segura de limpeza:

1. Revisar documentação histórica de features que ainda menciona exemplos pré-refactor
2. Fazer uma passada final para remover linguagem de transição agora obsoleta
