# Plano de Refatoracao da Arquitetura do Desktop App

Esta nota registra os principais pontos de acoplamento observados no Desktop App e propoe um plano incremental de refatoracao com baixo risco.

## Resumo

A arquitetura atual do Desktop App esta funcional e melhor organizada do que um runtime desktop monolitico. Ha composition root dedicada, reaproveitamento de logica compartilhada em `src/application/`, adapters separados e cobertura relevante em `tests/unit/desktop/`.

O ponto principal nao e fazer uma reescrita. O melhor caminho e reduzir acoplamentos aos poucos, extraindo primeiro responsabilidades que ja estao misturadas entre runtime, GUI, persistencia e integracoes HTTP.

## Pontos de melhoria

### 1. `src/desktop/app/desktop_app.py` concentra responsabilidade demais

Hoje o runtime central acumula:

- inicializacao
- loop principal
- integracao com tray
- abertura da GUI
- reconfiguracao
- shutdown
- leitura de status

Impacto arquitetural:

- aumenta o acoplamento entre ciclo de vida, UI e servicos
- dificulta testes mais focados
- transforma o arquivo em ponto unico de mudanca

Melhoria desejada:

- separar lifecycle/runtime de coordenacao de UI e tray
- manter `DesktopApp` como orquestrador fino

### 2. `src/desktop/gui/simple_gui.py` virou modulo grande demais

Hoje esse arquivo concentra:

- configuracao em console
- setup inicial
- formulario GUI
- painel principal
- ponte de logs para a UI
- selecao de interface

Impacto arquitetural:

- alto acoplamento interno na camada de GUI
- manutencao mais dificil
- risco de misturar regras de uso com detalhes de widget

Melhoria desejada:

- dividir em modulos menores por responsabilidade
- separar forms, main window e helpers de logging/UI

### 3. `src/desktop/app/desktop_actions.py` acopla orquestracao a implementacoes concretas

Hoje a camada de acoes/coordenacao depende diretamente de:

- `HttpDiscordBotClient`
- `ConfigurationRepository`
- `EnvironmentUpdater`
- `ConfigurationService`

Impacto arquitetural:

- a orquestracao fica presa a detalhes concretos do desktop
- fica mais dificil mover regras compartilhaveis para `src/application/`
- testes dependem mais de monkeypatch do que de portas explicitas

Melhoria desejada:

- introduzir portas ou use cases para:
  - testar conexao com bot
  - enviar mensagem de teste
  - consultar canal detectado
  - persistir e aplicar configuracao

### 4. `src/desktop/services/tts_services.py` ainda mistura selecao de engine com regra de fluxo

Parte da logica de TTS ja foi extraida para `src/application/`, o que e um bom sinal. Ainda assim, o service desktop continua acumulando:

- criacao de engines
- fallback
- preparo de texto
- status de disponibilidade
- detalhes concretos de adapter

Impacto arquitetural:

- mantem regra demais na camada desktop
- dificulta reaproveitamento de regras em outros entrypoints

Melhoria desejada:

- mover mais decisao de fluxo para `src/application/`
- deixar no desktop apenas adapters e factories concretas

### 5. `src/desktop/adapters/system_tray.py` ainda tem fallback de encerramento agressivo

O uso de `os._exit(0)` no fallback do tray deve ser tratado como ultimo recurso.

Impacto arquitetural:

- bypass do shutdown coordenado
- reduz previsibilidade do encerramento

Melhoria desejada:

- concentrar encerramento no runtime principal
- manter o adapter apenas como emissor de callback

## Plano incremental

Classificacao do trabalho:

- refatoracao estrutural
- objetivo principal: reduzir acoplamento
- mudancas devem ser pequenas, reversiveis e preservando comportamento

### Etapa 1. Extrair coordenacao de acoes do bot para use cases/ports

Objetivo:

- remover dependencia direta de `DesktopBotActions` em `HttpDiscordBotClient`

Passos:

1. Criar portas neutras para operacoes de bot usadas pelo desktop
2. Criar use cases em `src/application/` para:
   - health check
   - envio de teste curto
   - consulta de voice context
3. Adaptar `HttpDiscordBotClient` para implementar a porta
4. Fazer `DesktopBotActions` delegar para os use cases

Arquivos provaveis:

- `src/application/`
- `src/desktop/app/desktop_actions.py`
- `src/desktop/services/discord_bot_client.py`

Validacao:

- `tests/unit/desktop/test_apps.py`
- `tests/unit/desktop/test_tts_services.py`
- startup do desktop continua funcionando

### Etapa 2. Extrair aplicacao de configuracao para uma camada mais explicita

Objetivo:

- reduzir o acoplamento entre UI, persistencia, atualizacao de ambiente e rebuild de servicos

Passos:

1. Introduzir uma porta para persistencia de configuracao desktop
2. Introduzir um servico ou use case para validar, persistir e aplicar configuracao
3. Deixar `DesktopConfigurationCoordinator` apenas coordenar fluxo de tela
4. Centralizar efeitos colaterais de config em um ponto explicito

Arquivos provaveis:

- `src/desktop/app/desktop_actions.py`
- `src/desktop/config/repository.py`
- `src/desktop/config/environment.py`
- possivel novo modulo em `src/application/` ou `src/desktop/app/`

Validacao:

- `tests/unit/desktop/test_apps.py`
- `tests/unit/desktop/test_desktop_config.py`
- salvar configuracao pela GUI
- reconfigurar via tray

### Etapa 3. Quebrar `simple_gui.py` em modulos menores

Objetivo:

- reduzir acoplamento interno da camada de GUI sem mudar comportamento

Passos:

1. Extrair configuracao em console para modulo proprio
2. Extrair formulario de configuracao GUI para modulo proprio
3. Extrair `DesktopAppMainWindow` para modulo proprio
4. Extrair `UILogHandler` e helpers visuais para modulo proprio
5. Manter uma facade pequena para imports existentes durante a transicao

Arquivos provaveis:

- `src/desktop/gui/simple_gui.py`
- novos modulos em `src/desktop/gui/`

Validacao:

- `tests/unit/desktop/test_simple_gui.py`
- `tests/unit/desktop/test_configuration_gui.py`
- abertura do painel principal
- salvamento de configuracao

### Etapa 4. Dividir o runtime principal do desktop

Objetivo:

- fazer `DesktopApp` voltar a ser um orquestrador menor

Passos:

1. Extrair um coordenador de lifecycle
2. Extrair um coordenador de tray/UI actions
3. Extrair montagem de status para objeto/helper dedicado
4. Deixar `DesktopApp` compor esses objetos

Arquivos provaveis:

- `src/desktop/app/desktop_app.py`
- novos modulos em `src/desktop/app/`

Validacao:

- `tests/unit/desktop/test_apps.py`
- `tests/unit/desktop/test_bootstrap.py`
- startup do desktop
- fechamento via tray
- reconfiguracao com hotkeys ativas

### Etapa 5. Empurrar mais regra de TTS para `src/application/`

Objetivo:

- reduzir regra de fluxo dentro de `src/desktop/services/tts_services.py`

Passos:

1. Definir portas neutras para engines e status
2. Extrair composicao de fallback/status para `src/application/`
3. Deixar no desktop apenas factories/adapters concretas

Arquivos provaveis:

- `src/application/`
- `src/desktop/services/tts_services.py`
- possivelmente `src/infrastructure/tts/`

Validacao:

- `tests/unit/desktop/test_tts_services.py`
- fluxo de captura + reproducao
- fallback Discord/local

### Etapa 6. Limpar fallback de encerramento do tray

Objetivo:

- remover encerramento abrupto do adapter

Passos:

1. Fazer o tray depender sempre de callback de quit
2. Tratar ausencia de callback como no-op seguro ou log
3. Garantir que o encerramento coordenado continue no runtime

Arquivos provaveis:

- `src/desktop/adapters/system_tray.py`
- `src/desktop/services/notification_services.py`
- `src/desktop/app/desktop_app.py`

Validacao:

- `tests/unit/desktop/test_notification_services.py`
- fechamento pelo tray

## Ordem recomendada

Prioridade sugerida:

1. extrair use cases/ports das acoes do bot
2. extrair aplicacao de configuracao
3. quebrar `simple_gui.py`
4. dividir `desktop_app.py`
5. mover mais regra de TTS para `src/application/`
6. limpar encerramento do tray

Essa ordem reduz risco porque primeiro desacopla fluxos e contratos, depois mexe nos modulos maiores.

## Arquivos mais sensiveis

- `app.py`
- `src/desktop/app/bootstrap.py`
- `src/desktop/app/desktop_app.py`
- `src/desktop/app/desktop_actions.py`
- `src/desktop/gui/simple_gui.py`
- `src/desktop/services/tts_services.py`
- `src/desktop/services/discord_bot_client.py`
- `src/desktop/adapters/system_tray.py`

## Checklist de validacao por iteracao

Para cada etapa relevante:

- rodar testes unitarios de desktop afetados
- verificar imports e boundaries
- validar startup do desktop
- validar fluxo de hotkey
- validar configuracao via GUI quando a etapa tocar UI
- validar tray quando a etapa tocar notificacoes ou encerramento
- confirmar que o bot continua iniciando independentemente do desktop

## Fora de escopo por enquanto

- reescrita completa do desktop
- migracao grande de framework GUI
- unificacao forcada de todo codigo desktop com o bot

## Resultado esperado

Ao final dessas etapas, o desktop deve ficar:

- mais facil de testar
- com menos acoplamento entre runtime, GUI e infraestrutura
- com regras compartilhaveis mais proximas de `src/application/`
- mais seguro para continuar evoluindo sem concentrar logica em poucos arquivos
