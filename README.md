# python-tts-discord-bot

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7ed90fe1cc6f4090a7386df4681df463)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/7ed90fe1cc6f4090a7386df4681df463)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

Projeto com dois aplicativos independentes:

- Bot do Discord para entrar em canal de voz e reproduzir TTS
- Desktop App Windows com hotkeys para capturar texto e enviar ao bot

O repositorio segue Clean Architecture e busca reutilizar logica entre os dois
fluxos, sem duplicacao entre o runtime interno do Desktop App em `src/desktop`
e o restante de `src`.

## Estrutura rapida

- `src/bot.py`: sobe o bot do Discord e o servidor HTTP
- `app.py`: inicia o Desktop App Windows
- `src/`: camadas principais da aplicacao
- `docs/`: documentacao complementar
- `docs/BUILD_GUIDE.md`: guia de build do executavel Windows

## Requisitos

- Python 3.11+
- `ffmpeg` para o fluxo de voz do Discord
- O ambiente virtual `.venv` faz parte da instalacao

Instalacao basica:

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
winget install ffmpeg
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Para voz no Discord localmente, tambem pode ser necessario:

```bash
pip install pynacl
```

Para o passo a passo completo, consulte [docs/SETUP.md](docs/SETUP.md).

## Execucao rapida

Configure um arquivo `.env` com pelo menos:

```env
DISCORD_TOKEN=seu_token_aqui
DISCORD_BOT_URL=http://127.0.0.1:10000
DISCORD_BOT_PORT=10000
```

Suba o bot:

```bash
python -m src.bot
```

Em outro terminal, rode o Desktop App:

```bash
python app.py
```

## Testes

```bash
pytest
```

Detalhes de estrutura e execucao estao em [docs/TESTING.md](docs/TESTING.md).

## Build do executavel Windows

No Windows, use o script oficial:

```powershell
./scripts/build/build_clean_architecture.ps1
```

No Linux, gere o `.exe` pelo workflow de CI que roda em ambiente Windows.

## Documentacao

Use o README principal como ponto de entrada e deixe os detalhes nos guias
especificos. A pasta `docs/` fica reservada para estrutura principal e guias
duraveis; documentacao de novas features deve ir em `docs/features/`.

- [Indice da documentacao](docs/README.md)
- [Guia de setup do ambiente](docs/SETUP.md)
- [Guia de testes](docs/TESTING.md)
- [Deploy do bot como servico Windows com WinSW](docs/WINDOWS_BOT_SERVICE.md)
- [Constituicao e workflow canonicos](.specify/README.md)
- [Guia de build do executavel Windows](docs/BUILD_GUIDE.md)
- [Arquitetura do projeto](docs/ARCHITECTURE.md)
- [Fluxos de runtime e composition roots](docs/RUNTIME_FLOWS.md)
- [Guia de transicoes arquiteturais e compatibilidade temporaria](docs/ARCHITECTURE_TRANSITIONS.md)
- [Mapa de onde mexer por tipo de mudanca](docs/CHANGE_MAP.md)
- [Checklist curto de review tecnico](docs/REVIEW_CHECKLIST.md)
- [Regra de limpeza de transicoes temporarias](docs/TRANSITION_CLEANUP.md)
- [Exemplos de onde comecar por tipo de mudanca](docs/CHANGE_EXAMPLES.md)
- [Guia do Desktop App](docs/README_DESKTOP_APP.md)
- [Configuracao de hotkeys](docs/HOTKEY_SETUP.md)

## Observacoes

- Nao versione o `DISCORD_TOKEN`
- O bot e o Desktop App devem continuar funcionando de forma independente
- Prefira consultar `docs/` para detalhes de arquitetura, setup e troubleshooting
