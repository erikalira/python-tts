# Arquitetura do Projeto - Desktop App Windows e Bot Discord

## Visao geral

Este projeto contem dois aplicativos independentes:

1. Bot do Discord com endpoint HTTP para TTS
2. Desktop App Windows com hotkeys, GUI e system tray

Ambos seguem Clean Architecture e os principios SOLID para manter:

- baixo acoplamento entre camadas
- alta coesao dentro dos modulos
- reuso de regras compartilhadas em `src/application/` e `src/core/`
- independencia entre o bot e o Desktop App

## Diagramas

Para leitura visual da arquitetura, use os diagramas curados em vez do output bruto do `pyreverse`:

- [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)
- [diagrams/layer-overview.md](diagrams/layer-overview.md)
- [diagrams/shared-tts-core.md](diagrams/shared-tts-core.md)
- [diagrams/bot-runtime.md](diagrams/bot-runtime.md)
- [diagrams/desktop-runtime.md](diagrams/desktop-runtime.md)

Esses diagramas foram organizados por camada e contexto de runtime para ficarem legiveis como documentacao duravel.

## Entry points

### Desktop App

- entry point oficial: `app.py`
- runtime interno: `src/desktop/`
- composition root: `src/desktop/app/bootstrap.py`
- runtime principal: `src/desktop/app/desktop_app.py`

### Bot Discord

- entry point oficial: `src/bot.py`
- servidor HTTP: `src/infrastructure/http/server.py`
- bind HTTP local por padrao em `127.0.0.1`; para expor externamente em deploy, configure `DISCORD_BOT_HOST=0.0.0.0`

## Estrutura principal

```text
src/
  core/                  # entidades, value objects, interfaces puras
  application/           # casos de uso e orquestracao compartilhada
  infrastructure/        # integracoes externas e IO
  presentation/          # controllers e fluxos de entrada
  desktop/               # runtime interno do Desktop App
    adapters/            # teclado, tray, TTS local
    app/                 # bootstrap e runtime principal do Desktop App
    config/              # DesktopAppConfig, repository, validation, environment
    gui/                 # interfaces e janelas do Desktop App
    services/            # hotkeys, notifications e engines do Desktop App
```

## Desktop App

### Config

O Desktop App usa `DesktopAppConfig` como container principal de configuracao.

```python
@dataclass
class DesktopAppConfig:
    tts: TTSConfig
    discord: DiscordConfig
    hotkey: HotkeyConfig
    interface: InterfaceConfig
    network: NetworkConfig
```

Arquivos principais:

- `src/desktop/config/desktop_config.py`
- `src/desktop/config/models.py`
- `src/desktop/config/repository.py`
- `src/desktop/config/validation.py`

O ambiente local e carregado a partir de `.env`, usado como base para defaults do Desktop App e para reproduzir comportamento em desenvolvimento e em parte dos testes.

### Runtime

O runtime principal do Desktop App fica em `src/desktop/app/desktop_app.py`.

Responsabilidades principais:

- carregar configuracao
- montar TTS, hotkeys e tray
- abrir o painel principal quando Tkinter estiver disponivel
- coordenar reconfiguracao sem misturar regra de negocio com GUI

### TTS e hotkeys

O Desktop App foi separado em responsabilidades menores:

- `src/desktop/app/tts_runtime.py`: threading, cleanup e feedback de execucao
- `src/desktop/services/tts_services.py`: engines e selecao de entrega de TTS
- `src/desktop/services/hotkey_services.py`: monitor e gerenciamento de hotkeys
- `src/desktop/services/hotkey_capture.py`: estado puro de captura de texto

## Regras de dependencia

- `src/core/` nao depende de camadas externas
- `src/application/` depende apenas de `src/core/`
- `src/infrastructure/` pode depender de `application` e `core`
- `src/presentation/` delega para `application`
- `src/desktop/` deve conter apenas runtime, adapters e coordenacao especifica do Desktop App
- logica compartilhavel entre bot e Desktop App deve ser extraida para `src/application/` ou `src/core/`

## Execucao

```bash
# Bot
python -m src.bot

# Desktop App
python app.py
```

## Testes

Os testes do Desktop App ficam em `tests/unit/desktop/`.

Observacoes:

- a pasta de testes do Desktop App foi padronizada para `tests/unit/desktop/`
- os simbolos publicos do codigo foram padronizados para `Desktop App`
- o ambiente local de testes usa `.env` como base para parte dos defaults e cenarios

## Referencias

- [../desktop/DESKTOP_APP_GUIDE.md](../desktop/DESKTOP_APP_GUIDE.md)
