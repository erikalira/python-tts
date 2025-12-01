# 🚀 Como Criar Executável do TTS Hotkey para Windows

Este guia explica como criar o executável standalone do TTS Hotkey para Windows.

## 📋 Pré-requisitos

- Python 3.8+ instalado no Windows
- Dependências instaladas via `pip install -r requirements.txt`
- Windows 10/11

## 🎯 TTS Hotkey Configurável

- **Arquivo**: `tts_hotkey_configurable.py`
- **Características**: Interface gráfica Tkinter completa, configuração visual
- **Tamanho**: ~15MB
- **Ideal para**: Desktop Windows, usuários finais, máxima facilidade de uso

## ⚡ Compilação para Windows

### Método 1: Script Automático (Recomendado)

```powershell
# Execute no PowerShell como administrador
scripts\build\build_configurable.ps1
```

### Método 2: Compilação Manual

```powershell
# Instalar PyInstaller
pip install pyinstaller

# Compilar o executável
pyinstaller --onefile `
    --hidden-import=keyboard `
    --hidden-import=pyttsx3 `
    --hidden-import=gtts `
    --hidden-import=requests `
    --hidden-import=tkinter `
    --hidden-import=tkinter.ttk `
    --hidden-import=tkinter.messagebox `
    --name=tts_hotkey_configurable `
    --windowed `
    tts_hotkey_configurable.py
```

## 📁 Localização do Executável

Após a compilação, o executável fica em:

```
dist/
└── tts_hotkey_configurable.exe  # Executável para Windows
```

## 📦 Dependências Incluídas

O executável inclui automaticamente:

- **Core**: Python runtime, bibliotecas padrão
- **TTS**: pyttsx3, gTTS, requests
- **Hotkeys**: keyboard (captura de teclas)
- **Interface**: tkinter (interface gráfica)
- **HTTP**: requests, urllib3, certifi

## 🎮 Como Usar o Executável

### Primeira Execução

```powershell
# Executar o programa
cd dist
.\tts_hotkey_configurable.exe
```

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
