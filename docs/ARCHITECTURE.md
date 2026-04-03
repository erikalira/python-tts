# Arquitetura do Projeto - TTS Hotkey Windows

## VisÃ£o geral

Este projeto contÃ©m dois aplicativos independentes:

1. Bot do Discord com endpoint HTTP para TTS
2. Desktop App Windows com hotkeys, GUI e system tray

Ambos seguem Clean Architecture e os princÃ­pios SOLID para manter:

- baixo acoplamento entre camadas
- alta coesÃ£o dentro dos mÃ³dulos
- reuso de regras compartilhadas em `src/application/` e `src/core/`
- independÃªncia entre o bot e o Desktop App

## Entry points

### Desktop App

- entry point oficial: `app.py`
- runtime interno: `src/desktop/`
- composition root: `src/desktop/app/bootstrap.py`
- runtime principal: `src/desktop/app/desktop_app.py`

### Bot Discord

- entry point oficial: `src/bot.py`
- servidor HTTP: `src/infrastructure/http/server.py`

## Estrutura principal

```text
src/
  core/                  # entidades, value objects, interfaces puras
  application/           # casos de uso e orquestraÃ§Ã£o compartilhada
  infrastructure/        # integraÃ§Ãµes externas e IO
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

O Desktop App usa `DesktopAppConfig` como container principal de configuraÃ§Ã£o.

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

O ambiente local Ã© carregado a partir de `.env`, usado como base para defaults do Desktop App e para reproduzir comportamento em desenvolvimento e em parte dos testes.

### Runtime

O runtime principal do Desktop App fica em `src/desktop/app/desktop_app.py`.

Responsabilidades principais:

- carregar configuraÃ§Ã£o
- montar TTS, hotkeys e tray
- abrir o painel principal quando Tkinter estiver disponÃ­vel
- coordenar reconfiguraÃ§Ã£o sem misturar regra de negÃ³cio com GUI

### TTS e hotkeys

O Desktop App foi separado em responsabilidades menores:

- `src/desktop/app/tts_runtime.py`: threading, cleanup e feedback de execuÃ§Ã£o
- `src/desktop/services/tts_services.py`: engines e seleÃ§Ã£o de entrega de TTS
- `src/desktop/services/hotkey_services.py`: monitor e gerenciamento de hotkeys
- `src/desktop/services/hotkey_capture.py`: estado puro de captura de texto

## Regras de dependÃªncia

- `src/core/` nÃ£o depende de camadas externas
- `src/application/` depende apenas de `src/core/`
- `src/infrastructure/` pode depender de `application` e `core`
- `src/presentation/` delega para `application`
- `src/desktop/` deve conter apenas runtime, adapters e coordenaÃ§Ã£o especÃ­fica do Desktop App
- lÃ³gica compartilhÃ¡vel entre bot e Desktop App deve ser extraÃ­da para `src/application/` ou `src/core/`

## ExecuÃ§Ã£o

```bash
# Bot
python -m src.bot

# Desktop App
python app.py
```

## Testes

Os testes do Desktop App ficam em `tests/unit/desktop/`.

ObservaÃ§Ãµes:

- a pasta de testes do Desktop App foi padronizada para `tests/unit/desktop/`
- os sÃ­mbolos pÃºblicos do cÃ³digo foram padronizados para `Desktop App`
- o ambiente local de testes usa `.env` como base para parte dos defaults e cenÃ¡rios

## ReferÃªncias

- [README_DESKTOP_APP.md](README_DESKTOP_APP.md)
- [features/DESKTOP_APP_MAIN_PANEL.md](features/DESKTOP_APP_MAIN_PANEL.md)
- [features/DESKTOP_APP_GUI_UX.md](features/DESKTOP_APP_GUI_UX.md)

