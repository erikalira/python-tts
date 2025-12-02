# 🚀 Como Criar Executável do TTS Hotkey para Windows

Este guia explica como criar o executável standalone do TTS Hotkey para Windows com **Clean Architecture** e **SOLID principles**.

## 📋 Pré-requisitos

- Python 3.8+ instalado no Windows
- Dependências instaladas via `pip install -r requirements.txt`
- Windows 10/11

## 🎯 TTS Hotkey Clean Architecture

- **Arquivo**: `tts_hotkey_configurable.py`
- **Arquitetura**: Clean Architecture completa com SOLID principles
- **Características**:
  - Interface gráfica Tkinter com system tray
  - Configuração persistente com JSON
  - Dependency injection em todas as camadas
  - Automatic fallback se clean architecture falhar
- **Tamanho**: ~20MB
- **Ideal para**: Desktop Windows, desenvolvimento profissional, máxima robustez

## ⚡ Compilação para Windows

### Método 1: Clean Architecture Build (Recomendado)

```powershell
# Execute no PowerShell
scripts\build\build_clean_architecture.ps1

# Ou usando Makefile (se disponível)
make build-clean
```

**Funcionalidades incluídas:**

- ✅ Clean Architecture completa
- ✅ Sistema de configuração com dataclasses
- ✅ Repository pattern para persistência
- ✅ Service layer com dependency injection
- ✅ Interface gráfica integrada
- ✅ System tray e notificações
- ✅ Fallback automático para versão embedded

### Método 2: Compilação Manual (Clean Architecture)

```powershell
# Instalar dependências
pip install pyinstaller keyboard pyttsx3 gtts requests pystray pillow

# Compilar com Clean Architecture
pyinstaller --onefile `
    --console `
    --name=tts_hotkey_clean `
    --hidden-import=keyboard `
    --hidden-import=pystray `
    --hidden-import=PIL `
    --hidden-import=pyttsx3 `
    --hidden-import=gtts `
    --hidden-import=requests `
    --hidden-import=tkinter `
    --hidden-import=tkinter.ttk `
    --hidden-import=tkinter.messagebox `
    tts_hotkey_configurable.py
```

### Método 3: Build Tradicional (Fallback)

```powershell
# Para build sem clean architecture (compatibilidade)
scripts\build\build_configurable.ps1
```

## 📁 Localização do Executável

Após a compilação, o executável fica em:

```
dist/
├── tts_hotkey_clean.exe          # Clean Architecture (Recomendado)
├── run_tts_hotkey_clean.bat      # Script de execução automático
└── tts_hotkey_configurable.exe   # Versão tradicional (fallback)
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

### Primeira Execução (Clean Architecture)

```powershell
# Executar versão Clean Architecture
cd dist
.\tts_hotkey_clean.exe

# Ou usar o script automático
.\run_tts_hotkey_clean.bat
```

**Primeira execução fará:**

1. ✅ Carregará configuração padrão ou existing config
2. ✅ Oferecerá interface gráfica de configuração (Tkinter)
3. ✅ Salvará configurações em JSON persistente
4. ✅ Iniciará system tray com ícone
5. ✅ Ativará hotkeys globais
6. ✅ Mostrará status no console e notificações

### Configuração

1. **Discord User ID**: Obter em Discord > Configurações > Avançado > Modo Desenvolvedor
2. **Engine TTS**: Escolher entre pyttsx3 (local), gtts (Google) ou discord (via bot)
3. **Hotkeys**: Definir caracteres de abertura/fechamento (padrão: `{` e `}`)
4. **Velocidade**: Ajustar velocidade da fala (apenas pyttsx3)

### Uso Normal

1. Executar o programa
2. Configurar na interface gráfica
3. Digitar texto entre os caracteres configurados
4. Exemplo: `{Olá mundo}` → Fala "Olá mundo"

## 🔍 Resolução de Problemas

### Dependências Faltando

```powershell
# Instalar todas as dependências
pip install -r requirements.txt

# Instalar PyInstaller
pip install pyinstaller
```

### Executável Muito Grande

- Use compactação: adicione `--upx-dir=caminho\para\upx`
- Exclua módulos desnecessários: `--exclude-module=nome_do_modulo`

### Erro de Importação

- Adicione `--hidden-import=nome_do_modulo` no comando PyInstaller
- Verifique se todas as dependências estão instaladas

### Antivírus Blocking

- Adicione exceção para a pasta `dist/`
- Use certificado de código para assinar o executável

## 🚀 Distribuição

O executável é standalone e pode ser distribuído:

1. **Copiar apenas o .exe** para qualquer Windows 10/11
2. **Executar diretamente** - não precisa Python instalado
3. **Configurar na primeira execução** através da interface gráfica

## 📝 Logs e Debug

Para debug avançado:

```powershell
# Executar com console para ver logs
pyinstaller --onefile --console tts_hotkey_configurable.py

# Logs detalhados do PyInstaller
pyinstaller --log-level=DEBUG --onefile tts_hotkey_configurable.py
```

## 🎯 Vantagens do Executável Windows

- **Interface Gráfica**: Fácil configuração visual
- **Standalone**: Um único arquivo .exe
- **Portável**: Funciona sem instalação
- **Completo**: Todas as funcionalidades incluídas
- **Windows Nativo**: Integração completa com o sistema
