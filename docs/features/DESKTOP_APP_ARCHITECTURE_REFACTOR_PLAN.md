# Plano de Refatoracao da Arquitetura do Desktop App

Esta nota registra os principais pontos de acoplamento observados no Desktop App e o plano incremental usado para reduzi-los com baixo risco.

## Resumo

A arquitetura do Desktop App ja estava funcional, com composition root dedicada, reaproveitamento de logica compartilhada em `src/application/`, adapters separados e boa cobertura em `tests/unit/desktop/`.

O objetivo deste plano foi reduzir acoplamentos de forma incremental, sem reescrita ampla, preservando a independencia entre o Desktop App e o bot do Discord.

## Pontos de melhoria observados

### 1. `src/desktop/app/desktop_app.py` concentrava responsabilidade demais

Sintomas observados:

- inicializacao
- loop principal
- integracao com tray
- abertura da GUI
- reconfiguracao
- shutdown
- leitura de status

Melhoria aplicada:

- extracao de coordenadores de lifecycle, status e acoes de UI/tray

Status:

- concluido

### 2. A GUI desktop estava concentrada em um modulo grande demais

Sintomas observados:

- configuracao em console
- setup inicial
- formulario GUI
- painel principal
- ponte de logs para a UI
- selecao de interface

Melhoria aplicada:

- separacao em `config_dialogs.py`, `main_window.py`, `configuration_service.py`, `ui_logging.py` e `tk_support.py`
- remocao da facade legado `simple_gui.py`

Status:

- concluido

### 3. `src/desktop/app/desktop_actions.py` estava acoplado a implementacoes concretas

Sintomas observados:

- dependencia direta de client HTTP concreto
- mistura de coordenacao com persistencia/aplicacao de configuracao

Melhoria aplicada:

- extracao de use cases para acoes do bot em `src/application/desktop_bot.py`
- extracao da aplicacao de configuracao para `src/desktop/app/configuration_application.py`

Status:

- concluido

### 4. `src/desktop/services/tts_services.py` ainda misturava adapters com regra de fluxo

Sintomas observados:

- fallback
- preparo de texto
- disponibilidade
- payload de status

Melhoria aplicada:

- extracao para `src/application/desktop_tts.py`
- desktop mantendo apenas adapters, factories e gateway de status

Status:

- concluido

### 5. `src/desktop/adapters/system_tray.py` tinha fallback de encerramento agressivo

Sintoma observado:

- uso de `os._exit(0)` fora do shutdown coordenado

Melhoria aplicada:

- remocao do encerramento abrupto
- fallback seguro com ocultacao do tray e log quando `quit_handler` nao estiver ligado

Status:

- concluido

## Etapas executadas

### Etapa 1. Extrair coordenacao de acoes do bot para use cases/ports

Status:

- concluida

Mudancas principais:

1. Criacao de portas e use cases compartilhados em `src/application/desktop_bot.py`
2. Adaptacao de `HttpDiscordBotClient` para o contrato compartilhado
3. Delegacao de `DesktopBotActions` para use cases

Validacao executada:

- `tests/unit/application/test_desktop_bot.py`
- `tests/unit/desktop/test_apps.py`
- `tests/unit/desktop/test_tts_services.py`

### Etapa 2. Extrair aplicacao de configuracao para uma camada mais explicita

Status:

- concluida

Mudancas principais:

1. Criacao de `src/desktop/app/configuration_application.py`
2. `DesktopConfigurationCoordinator` reduzido a fluxo/orquestracao
3. Persistencia, validacao e aplicacao de configuracao centralizadas

Validacao executada:

- `tests/unit/desktop/test_configuration_application.py`
- `tests/unit/desktop/test_apps.py`

### Etapa 3. Quebrar a GUI em modulos menores

Status:

- concluida

Mudancas principais:

1. Extracao de dialogs e formularios para `src/desktop/gui/config_dialogs.py`
2. Extracao da janela principal para `src/desktop/gui/main_window.py`
3. Extracao da escolha de interface para `src/desktop/gui/configuration_service.py`
4. Extracao do suporte de Tk para `src/desktop/gui/tk_support.py`
5. Remocao dos wrappers legados `src/desktop/gui/simple_gui.py` e `src/desktop/gui/configuration_gui.py`

Validacao executada:

- `tests/unit/desktop/test_simple_gui.py`
- `tests/unit/desktop/test_configuration_gui.py`
- `tests/unit/desktop/test_bootstrap.py`

### Etapa 4. Dividir o runtime principal do desktop

Status:

- concluida

Mudancas principais:

1. Criacao de `runtime_lifecycle.py`
2. Criacao de `ui_tray_actions.py`
3. Criacao de `runtime_status.py`
4. `DesktopApp` reduzido a composicao e delegacao

Validacao executada:

- `tests/unit/desktop/test_apps.py`
- `tests/unit/desktop/test_bootstrap.py`

### Etapa 5. Empurrar mais regra de TTS para `src/application/`

Status:

- concluida

Mudancas principais:

1. Criacao de `src/application/desktop_tts.py`
2. Delegacao de fluxo e status de TTS pelo service desktop
3. Remocao de alias legado de service de TTS

Validacao executada:

- `tests/unit/application/test_desktop_tts.py`
- `tests/unit/desktop/test_tts_services.py`
- `tests/unit/desktop/test_apps.py`

### Etapa 6. Limpar fallback de encerramento do tray

Status:

- concluida

Mudancas principais:

1. Remocao de `os._exit(0)` do adapter do tray
2. Cobertura de fallback seguro quando nao houver `quit_handler`

Validacao executada:

- `tests/unit/desktop/test_notification_services.py`
- `tests/unit/desktop/test_apps.py`
- `tests/unit/desktop/test_bootstrap.py`

## Resultado final esperado

Ao final das etapas 1 a 6, o Desktop App ficou:

- mais facil de testar por camada
- com menos acoplamento entre runtime, GUI e infraestrutura
- com mais regra compartilhada em `src/application/`
- com menos wrappers de compatibilidade e menos codigo legado no caminho
- com encerramento mais previsivel e seguro
