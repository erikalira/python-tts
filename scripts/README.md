# Scripts Directory

Esta pasta contem scripts de build, teste manual e utilitarios para o TTS Hotkey.

## CompilaÃ§Ã£o para Windows

```powershell
# Build recomendado (Clean Architecture + SOLID principles)
powershell scripts/build/build_clean_architecture.ps1
```

O executÃ¡vel serÃ¡ criado em `dist/tts_hotkey_clean.exe`

## CaracterÃ­sticas IncluÃ­das

- âœ… Clean Architecture completa
- âœ… Interface grÃ¡fica Tkinter
- âœ… System tray e notificaÃ§Ãµes
- âœ… Multi-engine TTS (gTTS + pyttsx3)
- âœ… ConfiguraÃ§Ã£o persistente em AppData/Local/TTS-Hotkey/
- âœ… Hotkeys globais
- âœ… Entry point do Desktop App Ãºnico

### ðŸ› ï¸ Utils

- **create_icon.py**: Gera Ã­cones para os executÃ¡veis

### ðŸ§ª Testes manuais

- **scripts/test/manual_integration_check.py**: smoke check manual de integracao e dependencias
- **scripts/test/manual_security_check.py**: validacao manual do cenario de seguranca do bot

## Requisitos

### Para Scripts de Build

- **PowerShell** (pwsh ou powershell)
- **PyInstaller**: `pip install pyinstaller`
- **DependÃªncias**: Execute `pip install -r requirements.txt`

### Para Scripts de Teste

- **Pytest**: Para testes unitÃ¡rios
- **Python 3.8+**: VersÃ£o mÃ­nima suportada
- **VariÃ¡veis de ambiente**: Configure `.env` adequadamente

## Comandos RÃ¡pidos

```bash
# Instalar dependÃªncias
pip install -r requirements.txt
pip install -r requirements-test.txt

# Desenvolvimento diÃ¡rio com o ambiente virtual do projeto
./.venv/bin/python -m pytest tests

# Foco no Desktop App
./.venv/bin/python -m pytest tests/unit/desktop

# Build do executÃ¡vel no Windows
pwsh -File scripts/build/build_clean_architecture.ps1
```

## IntegraÃ§Ã£o com CI/CD

Os scripts foram projetados para funcionar tanto localmente quanto em ambientes de CI/CD:

- **GitHub Actions**: Use `scripts/build/build_clean_architecture.ps1`
- **Local Development**: Use comandos diretos de Python e PowerShell
- **Windows**: Use PowerShell para builds
- **Linux/macOS**: Use Python para desenvolvimento e o workflow Windows para gerar o `.exe`

## Troubleshooting

### PowerShell nÃ£o encontrado

```bash
# Ubuntu/Debian
sudo apt install powershell

# macOS
brew install powershell
```

### PermissÃµes no Linux

```bash
# Tornar scripts executÃ¡veis
chmod +x scripts.sh
chmod +x scripts/test/*.sh
```

### Erros de DependÃªncias

```bash
# Reinstalar dependÃªncias
pip install -r requirements.txt
pip install -r requirements-test.txt

# Ou verificar ambiente virtual
source .venv/bin/activate
pip list
```

## ContribuiÃ§Ã£o

Para adicionar novos scripts:

1. **Build scripts**: Adicione em `scripts/build/`
2. **Test scripts**: Adicione em `scripts/test/`
3. **Utils**: Adicione em `scripts/utils/`
4. **Atualize**: Modifique este README e a documentaÃ§Ã£o relacionada
5. **Documente**: Atualize este README

## Links Ãšteis

- [DocumentaÃ§Ã£o Principal](../README.md)
- [Arquitetura](../docs/ARCHITECTURE.md)
- [Troubleshooting](../docs/TROUBLESHOOTING.md)
- [Setup Hotkeys](../docs/HOTKEY_SETUP.md)

