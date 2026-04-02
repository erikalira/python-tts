# Scripts Directory

Esta pasta contem scripts de build, teste manual e utilitarios para o TTS Hotkey.

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
- ✅ Entry point standalone único

### 🛠️ Utils

- **create_icon.py**: Gera ícones para os executáveis

### 🧪 Testes manuais

- **scripts/test/manual_integration_check.py**: smoke check manual de integracao e dependencias
- **scripts/test/manual_security_check.py**: validacao manual do cenario de seguranca do bot

## Requisitos

### Para Scripts de Build

- **PowerShell** (pwsh ou powershell)
- **PyInstaller**: `pip install pyinstaller`
- **Dependências**: Execute `pip install -r requirements.txt`

### Para Scripts de Teste

- **Pytest**: Para testes unitários
- **Python 3.8+**: Versão mínima suportada
- **Variáveis de ambiente**: Configure `.env` adequadamente

## Comandos Rápidos

```bash
# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-test.txt

# Desenvolvimento diário com o ambiente virtual do projeto
./.venv/bin/python -m pytest tests

# Foco no standalone
./.venv/bin/python -m pytest tests/unit/standalone

# Build do executável no Windows
pwsh -File scripts/build/build_clean_architecture.ps1
```

## Integração com CI/CD

Os scripts foram projetados para funcionar tanto localmente quanto em ambientes de CI/CD:

- **GitHub Actions**: Use `scripts/build/build_clean_architecture.ps1`
- **Local Development**: Use comandos diretos de Python e PowerShell
- **Windows**: Use PowerShell para builds
- **Linux/macOS**: Use Python para desenvolvimento e o workflow Windows para gerar o `.exe`

## Troubleshooting

### PowerShell não encontrado

```bash
# Ubuntu/Debian
sudo apt install powershell

# macOS
brew install powershell
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
pip install -r requirements.txt
pip install -r requirements-test.txt

# Ou verificar ambiente virtual
source .venv/bin/activate
pip list
```

## Contribuição

Para adicionar novos scripts:

1. **Build scripts**: Adicione em `scripts/build/`
2. **Test scripts**: Adicione em `scripts/test/`
3. **Utils**: Adicione em `scripts/utils/`
4. **Atualize**: Modifique este README e a documentação relacionada
5. **Documente**: Atualize este README

## Links Úteis

- [Documentação Principal](../README.md)
- [Arquitetura](../docs/ARCHITECTURE.md)
- [Troubleshooting](../docs/TROUBLESHOOTING.md)
- [Setup Hotkeys](../docs/HOTKEY_SETUP.md)
