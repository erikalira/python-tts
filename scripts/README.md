# Scripts Directory

Esta pasta contém scripts de build, teste manual e utilitários para o Desktop App e para a operação do bot.

## Compilação para Windows

```powershell
# Build recomendado (Clean Architecture + SOLID principles)
powershell scripts/build/build_clean_architecture.ps1
```

O executável será criado em `dist/HotkeyTTS.exe`.

## Características Incluídas

- Clean Architecture completa
- Interface gráfica Tkinter
- System tray e notificações
- Multi-engine TTS (`gTTS` + `pyttsx3`)
- Configuração persistente em `AppData/Local/DesktopApp/`
- Hotkeys globais
- Entry point único do Desktop App

## Utils

- `create_icon.py`: gera ícones para os executáveis
- `backup_postgres.ps1`: gera backup lógico do Postgres em container com retenção local
- `restore_postgres.ps1`: restaura um backup `.dump` para o Postgres em container
- `dependency_maintenance.py`: inspeciona versões, reescreve constraints de `requirements*.txt` e executa validação pós-migração
- `migrate_json_config_to_postgres.py`: migra configs `guild_*.json` do bot para o backend Postgres

## Testes manuais

- `scripts/test/manual_integration_check.py`: smoke check manual de integração e dependências
- `scripts/test/manual_security_check.py`: validação manual do cenário de segurança do bot

## Requisitos

### Para scripts de build

- `PowerShell` (`pwsh` ou `powershell`)
- `PyInstaller`: `pip install pyinstaller`
- Dependências do projeto: `pip install -r requirements.txt`

### Para scripts de teste

- `Pytest`
- `Python 3.8+`
- Variáveis de ambiente configuradas adequadamente

## Comandos rápidos

```bash
# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-test.txt

# Desenvolvimento diário com o ambiente virtual do projeto
./.venv/bin/python -m pytest tests

# Foco no Desktop App
./.venv/bin/python -m pytest tests/unit/desktop

# Build do executável no Windows
pwsh -File scripts/build/build_clean_architecture.ps1
```

## Integração com CI/CD

Os scripts foram pensados para funcionar tanto localmente quanto em ambientes de CI/CD:

- GitHub Actions: use `scripts/build/build_clean_architecture.ps1`
- Local development: use comandos diretos de Python e PowerShell
- Windows: use PowerShell para builds
- Linux/macOS: use Python para desenvolvimento e o workflow Windows para gerar o `.exe`

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
chmod +x scripts.sh
chmod +x scripts/test/*.sh
```

### Erros de dependências

```bash
pip install -r requirements.txt
pip install -r requirements-test.txt

# Ou verificar ambiente virtual
source .venv/bin/activate
pip list
```

## Contribuição

Para adicionar novos scripts:

1. Adicione em `scripts/build/`, `scripts/test/` ou `scripts/utils/`
2. Atualize este README
3. Atualize a documentação relacionada quando necessário

## Links úteis

- [Documentação principal](../README.md)
- [Arquitetura](../docs/ARCHITECTURE.md)
- [Setup Hotkeys](../docs/HOTKEY_SETUP.md)
