# 🚀 Como Criar Executável do TTS Hotkey para Windows

Este guia explica como criar o executável do Desktop App TTS Hotkey para Windows com **Clean Architecture** e **SOLID principles**.

## 📋 Pré-requisitos

- Python 3.8+ instalado no Windows
- Dependências instaladas via `pip install -r requirements.txt`
- Windows 10/11

## 🎯 TTS Hotkey Clean Architecture

- **Arquivo**: `app.py`
- **Arquitetura**: Clean Architecture completa com SOLID principles
- **Características**:
  - Interface gráfica Tkinter com system tray
  - Configuração persistente com JSON
  - Dependency injection em todas as camadas
  - Automatic fallback se clean architecture falhar
- **Tamanho**: ~20MB
- **Ideal para**: Desktop Windows, desenvolvimento profissional, máxima robustez

## ⚡ Compilação para Windows

```powershell
# Execute no PowerShell (Windows 10+)
scripts\build\build_clean_architecture.ps1
```

**Funcionalidades incluídas automaticamente:**

- ✅ Clean Architecture completa
- ✅ Sistema de configuração com dataclasses
- ✅ Repository pattern para persistência
- ✅ Service layer com dependency injection
- ✅ Interface gráfica integrada (Tkinter)
- ✅ System tray e notificações
- ✅ Multi-engine TTS (gTTS + pyttsx3) com fallback automático

## 📁 Localização do Executável

Após a compilação:

```
dist/
├── tts_hotkey_clean.exe                # Executável principal para usuário final
└── run_tts_hotkey_clean_debug.bat      # Launcher auxiliar para troubleshooting
```

## 📦 Dependências Incluídas (Clean Architecture)

O executável inclui automaticamente:

- **Core**: Python runtime, bibliotecas padrão
- **Architecture**: Clean Architecture com SOLID principles
- **TTS**: pyttsx3, gTTS, requests (multi-engine com fallback)
- **Hotkeys**: keyboard (captura global de teclas)
- **System Integration**: pystray, PIL (system tray e notificações)
- **Interface**: tkinter (GUI de configuração)
- **Persistence**: JSON-based configuration repository
- **HTTP**: requests, urllib3, certifi
- **Platform Support**: Windows (full features), Linux (graceful degradation)

## 🎮 Como Usar o Executável

Após compilação, execute:

```powershell
cd dist
.\tts_hotkey_clean.exe
```

**Na primeira execução:**
1. Configuração de Discord User ID (Settings > Advanced > Developer Mode)
2. Escolher engine TTS (pyttsx3 local ou gTTS online)
3. Definir hotkeys (padrão: `{` abre, `}` fecha)
4. Salva configuração automaticamente
5. Inicia system tray com ícone

**Uso:** Digite `{seu texto}` para falar. Sistema roda em background.

## 🔍 Resolução de Problemas

| Problema | Solução |
|----------|---------|
| **Build falha** | Reinstale dependências: `pip install -r requirements.txt` |
| **Ícone não encontrado** | Está ok, build continua sem ícone |
| **PyInstaller não encontrado** | `pip install pyinstaller` |
| **Antivírus bloqueia .exe** | Adicione exceção para `dist/` folder |

## 🚀 Distribuição

O executável do Desktop App é **portável**:
- Cópie apenas `dist/tts_hotkey_clean.exe`
- Funciona em qualquer Windows 10/11
- Configure na primeira execução via interface gráfica
- Salva config automaticamente em `AppData/Local/TTS-Hotkey/`
- Abre como aplicativo de janela, sem console para o usuário final
