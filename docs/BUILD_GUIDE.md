# Como Criar Executavel do TTS Hotkey para Windows

Este guia explica como criar o executavel do Desktop App TTS Hotkey para Windows com Clean Architecture.

## Pre-requisitos

- Python 3.11+ instalado no Windows
- Windows 10/11
- `.venv` criado e ativado antes de instalar dependencias

Setup recomendado antes do build:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## TTS Hotkey Clean Architecture

- Arquivo: `app.py`
- Arquitetura: Clean Architecture
- Caracteristicas:
  - Interface grafica Tkinter com system tray
  - Configuracao persistente com JSON
  - Dependency injection nas camadas
  - Fallback automatico se a inicializacao principal falhar

## Compilacao para Windows

```powershell
scripts\build\build_clean_architecture.ps1
```

## Localizacao do Executavel

Apos a compilacao:

```text
dist/
|-- tts_hotkey_clean.exe
`-- run_tts_hotkey_clean_debug.bat
```

## Como Usar o Executavel

Depois do build:

```powershell
cd dist
.\tts_hotkey_clean.exe
```

Na primeira execucao:

1. Configure o Discord User ID
2. Escolha a engine TTS
3. Defina as hotkeys
4. Salve a configuracao
5. Inicie o app pela tray

## Resolucao de Problemas

| Problema | Solucao |
|----------|---------|
| Build falha | Ative o `.venv` e reinstale dependencias com `pip install -r requirements.txt` |
| Icone nao encontrado | O build pode continuar sem icone |
| PyInstaller nao encontrado | Com o `.venv` ativo, rode `pip install pyinstaller` |
| Antivirus bloqueia `.exe` | Adicione excecao para a pasta `dist/` |

## Distribuicao

O executavel do Desktop App e portatil:

- Copie `dist/tts_hotkey_clean.exe`
- Funciona em Windows 10/11
- Salva configuracao em `AppData/Local/TTS-Hotkey/`
