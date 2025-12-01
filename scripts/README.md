# Scripts Directory

Esta pasta contém todos os scripts organizados para facilitar o desenvolvimento e build do projeto Python TTS.

## Estrutura

```
scripts/
├── build/                  # Scripts de build/compilação
│   ├── build_exe.ps1          - Build padrão do executável
│   ├── build_exe_fixed.ps1    - Build com correções específicas
│   ├── build_standalone.ps1   - Build standalone (sem deps externas)
│   └── build_configurable.ps1 - Build versão configurável
├── test/                   # Scripts de teste
│   ├── test_improvements.sh   - Testa melhorias de performance
│   ├── test_config_gui.py     - Teste da GUI de configuração
│   └── test_discord_connection.py - Teste conexão Discord
├── utils/                  # Utilitários diversos
│   └── create_icon.py         - Criação de ícones
└── README.md              # Esta documentação
```

## Como Usar

### Opção 1: Makefile (Recomendado)

```bash
# Ver todos os comandos disponíveis
make help

# Exemplos comuns
make install        # Instalar dependências
make test          # Executar testes
make build-exe     # Build executável
make clean         # Limpar artifacts
```

### Opção 2: Script Bash

```bash
# Ver todos os comandos disponíveis
./scripts.sh help

# Exemplos comuns
./scripts.sh install        # Instalar dependências
./scripts.sh test          # Executar testes
./scripts.sh build-exe     # Build executável
./scripts.sh clean         # Limpar artifacts
```

### Opção 3: Scripts Diretos

#### Scripts de Build (PowerShell)

```powershell
# Build executável padrão
powershell scripts/build/build_exe.ps1

# Build standalone (recomendado para distribuição)
powershell scripts/build/build_standalone.ps1

# Build configurável (com GUI)
powershell scripts/build/build_configurable.ps1
```

#### Scripts de Teste

```bash
# Teste de melhorias
bash scripts/test/test_improvements.sh

# Teste GUI configuração
python scripts/test/test_config_gui.py

# Teste conexão Discord
python scripts/test/test_discord_connection.py
```

## Funcionalidades Principais

### 🔨 Build Scripts

- **build_exe.ps1**: Build padrão com PyInstaller
- **build_standalone.ps1**: Build completo sem dependências externas
- **build_configurable.ps1**: Build com interface de configuração
- **build_exe_fixed.ps1**: Build com correções específicas

### 🧪 Test Scripts

- **test_improvements.sh**: Analisa e testa melhorias de performance
- **test_config_gui.py**: Testa interface gráfica de configuração
- **test_discord_connection.py**: Valida conectividade Discord

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
