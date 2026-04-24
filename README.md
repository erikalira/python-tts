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
- `docs/desktop/WINDOWS_BUILD_GUIDE.md`: guia de build do executavel Windows

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

### Windows (CMD)

```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
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

Para o passo a passo completo, consulte [docs/getting-started/SETUP.md](docs/getting-started/SETUP.md).

## Execucao rapida

Configure um arquivo `.env` com pelo menos:

```env
DISCORD_TOKEN=seu_token_aqui
DISCORD_BOT_URL=http://127.0.0.1:10000
DISCORD_BOT_PORT=10000
```

Para usar fila Redis no bot localmente:

```bash
docker compose -f docker-compose.redis.yml up -d
```

E adicione ao `.env`:

```env
TTS_QUEUE_BACKEND=redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_KEY_PREFIX=tts
REDIS_COMPLETED_ITEM_TTL_SECONDS=900
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

Detalhes de estrutura e execucao estao em [docs/getting-started/TESTING.md](docs/getting-started/TESTING.md).

## Build do executavel Windows

No Windows, use o script oficial:

```powershell
./scripts/build/build_clean_architecture.ps1
```

No Linux, gere o `.exe` pelo workflow de CI que roda em ambiente Windows.

## Documentacao

Use o README principal como ponto de entrada e deixe os detalhes nos guias
especificos. A pasta `docs/` fica reservada para guias duraveis; artefatos de
planejamento e execucao de features devem ir em `specs/`.

- [Indice da documentacao](docs/README.md)
- [Guia de setup do ambiente](docs/getting-started/SETUP.md)
- [Guia de testes](docs/getting-started/TESTING.md)
- [Guia de deploy no servidor](docs/deploy/DEPLOYMENT_GUIDE.md)
- [Arquitetura do projeto](docs/architecture/ARCHITECTURE.md)
- [Guia do Desktop App](docs/desktop/DESKTOP_APP_GUIDE.md)
- [Constituicao e workflow canonicos](.specify/README.md)

## Governanca para contribuidores e IA

As regras canonicas de arquitetura, workflow e instrucao para agentes ficam em
`.specify/`.

- [Indice canonico de governanca](.specify/README.md)
- [Constituicao do repositorio](.specify/memory/constitution.md)
- [Checklist de review](.specify/review-checklist.md)
- [Resumo derivado para agentes](AGENTS.md)

## Observacoes

- Nao versione o `DISCORD_TOKEN`
- O bot e o Desktop App devem continuar funcionando de forma independente
- Prefira consultar `docs/` para detalhes de arquitetura, setup e troubleshooting
