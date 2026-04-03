# Arquitetura do Projeto - TTS Hotkey Windows

## Visão geral

Este projeto contém dois aplicativos independentes:

1. Bot do Discord com endpoint HTTP para TTS
2. Desktop App Windows com hotkeys, GUI e system tray

Ambos seguem Clean Architecture e os princípios SOLID para manter:

- baixo acoplamento entre camadas
- alta coesão dentro dos módulos
- reuso de regras compartilhadas em `src/application/` e `src/core/`
- independência entre o bot e o Desktop App

## Entry points

### Desktop App

- entry point oficial: `app.py`
- runtime interno: `src/standalone/`
- composition root: `src/standalone/app/bootstrap.py`
- runtime principal: `src/standalone/app/desktop_app.py`

### Bot Discord

- entry point oficial: `src/bot.py`
- servidor HTTP: `src/infrastructure/http/server.py`

## Estrutura principal

```text
src/
  core/                  # entidades, value objects, interfaces puras
  application/           # casos de uso e orquestração compartilhada
  infrastructure/        # integrações externas e IO
  presentation/          # controllers e fluxos de entrada
  standalone/            # runtime interno do Desktop App
    adapters/            # teclado, tray, TTS local
    app/                 # bootstrap e runtime principal do Desktop App
    config/              # DesktopAppConfig, repository, validation, environment
    gui/                 # interfaces e janelas do Desktop App
    services/            # hotkeys, notifications e engines do Desktop App
```

## Desktop App

### Config

O Desktop App usa `DesktopAppConfig` como container principal de configuração.

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

- `src/standalone/config/desktop_config.py`
- `src/standalone/config/models.py`
- `src/standalone/config/repository.py`
- `src/standalone/config/validation.py`

O ambiente local é carregado a partir de `.env`, usado como base para defaults do Desktop App e para reproduzir comportamento em desenvolvimento e em parte dos testes.

### Runtime

O runtime principal do Desktop App fica em `src/standalone/app/desktop_app.py`.

Responsabilidades principais:

- carregar configuração
- montar TTS, hotkeys e tray
- abrir o painel principal quando Tkinter estiver disponível
- coordenar reconfiguração sem misturar regra de negócio com GUI

### TTS e hotkeys

O Desktop App foi separado em responsabilidades menores:

- `src/standalone/app/tts_runtime.py`: threading, cleanup e feedback de execução
- `src/standalone/services/tts_services.py`: engines e seleção de entrega de TTS
- `src/standalone/services/hotkey_services.py`: monitor e gerenciamento de hotkeys
- `src/standalone/services/hotkey_capture.py`: estado puro de captura de texto

## Regras de dependência

- `src/core/` não depende de camadas externas
- `src/application/` depende apenas de `src/core/`
- `src/infrastructure/` pode depender de `application` e `core`
- `src/presentation/` delega para `application`
- `src/standalone/` deve conter apenas runtime, adapters e coordenação específica do Desktop App
- lógica compartilhável entre bot e Desktop App deve ser extraída para `src/application/` ou `src/core/`

## Execução

```bash
# Bot
python -m src.bot

# Desktop App
python app.py
```

## Testes

Os testes do Desktop App ficam em `tests/unit/standalone/`.

Observações:

- o nome da pasta de testes ainda é `standalone` por organização histórica
- os símbolos públicos do código foram padronizados para `Desktop App`
- o ambiente local de testes usa `.env` como base para parte dos defaults e cenários

## Referências

- [README_DESKTOP_APP.md](README_DESKTOP_APP.md)
- [features/DESKTOP_APP_MAIN_PANEL.md](features/DESKTOP_APP_MAIN_PANEL.md)
- [features/DESKTOP_APP_GUI_UX.md](features/DESKTOP_APP_GUI_UX.md)
