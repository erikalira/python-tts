# Scripts Directory

Esta pasta contém scripts de build para o TTS Hotkey.

## Compilação para Windows

```powershell
# Build recomendado (Clean Architecture + SOLID principles)
powershell scripts/build/build_clean_architecture.ps1
```

O executável será criado em `dist/tts_hotkey_clean.exe`

## Características Incluídas

- ✅ Clean Architecture completa
- ✅ Interface gráfica Tkinter
- ✅ System tray e notificações
- ✅ Multi-engine TTS (gTTS + pyttsx3)
- ✅ Configuração persistente em AppData/Local/TTS-Hotkey/
- ✅ Hotkeys globais
- ✅ Fallback automático

### 🛠️ Utils

- **create_icon.py**: Gera ícones para os executáveis

## Requisitos

### Para Scripts de Build

- **PowerShell** (pwsh ou powershell)
- **PyInstaller**: `pip install pyinstaller`
- **Dependências**: Execute `make install` primeiro

### Para Scripts de Teste

- **Pytest**: Para testes unitários
- **Python 3.8+**: Versão mínima suportada
- **Variáveis de ambiente**: Configure `.env` adequadamente

## Comandos Rápidos

```bash
# Setup completo
make setup && make dev

# Desenvolvimento diário
make test && make lint

# Build para produção
make build-standalone

# Limpeza geral
make clean
```

## Integração com CI/CD

Os scripts foram projetados para funcionar tanto localmente quanto em ambientes de CI/CD:

- **GitHub Actions**: Use os comandos make
- **Local Development**: Use ./scripts.sh ou make
- **Windows**: Use PowerShell para builds
- **Linux/macOS**: Use make ou bash scripts

## Troubleshooting

### PowerShell não encontrado

```bash
# Ubuntu/Debian
sudo apt install powershell

# macOS
brew install powershell

# Ou use scripts alternativos sem PS
./scripts.sh build-standalone  # Tentará usar python diretamente
```

### Permissões no Linux

```bash
# Tornar scripts executáveis
chmod +x scripts.sh
chmod +x scripts/test/*.sh
```

### Erros de Dependências

```bash
# Reinstalar dependências
make clean
make install

# Ou verificar ambiente virtual
source .venv/bin/activate
pip list
```

## Contribuição

Para adicionar novos scripts:

1. **Build scripts**: Adicione em `scripts/build/`
2. **Test scripts**: Adicione em `scripts/test/`
3. **Utils**: Adicione em `scripts/utils/`
4. **Atualize**: Modifique `Makefile` e `scripts.sh`
5. **Documente**: Atualize este README

## Links Úteis

- [Documentação Principal](../README.md)
- [Arquitetura](../docs/ARCHITECTURE.md)
- [Troubleshooting](../docs/TROUBLESHOOTING.md)
- [Setup Hotkeys](../docs/HOTKEY_SETUP.md)
