# python-tts-discord-bot

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7ed90fe1cc6f4090a7386df4681df463)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/7ed90fe1cc6f4090a7386df4681df463)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

Projeto com dois aplicativos independentes:

- Bot do Discord para entrar em canal de voz e reproduzir TTS
- Desktop App Windows com hotkeys para capturar texto e enviar ao bot

O repositÃ³rio segue Clean Architecture e busca reutilizar lÃ³gica entre os dois fluxos, sem duplicaÃ§Ã£o entre o runtime interno do Desktop App em `src/desktop` e o restante de `src`.

## Estrutura rÃ¡pida

- `src/bot.py`: sobe o bot do Discord e o servidor HTTP
- `app.py`: inicia o Desktop App Windows
- `src/`: camadas principais da aplicaÃ§Ã£o
- `docs/`: documentaÃ§Ã£o complementar
- `docs/BUILD_GUIDE.md`: guia de build do executÃ¡vel Windows

## Requisitos

- Python 3.11+
- `ffmpeg` para o fluxo de voz do Discord
- Ambiente virtual recomendado

InstalaÃ§Ã£o bÃ¡sica:

```bash
pip install -r requirements.txt
```

Para voz no Discord localmente, tambÃ©m pode ser necessÃ¡rio:

```bash
pip install pynacl
```

## ExecuÃ§Ã£o rÃ¡pida

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

## Build do executavel Windows

No Windows, use o script oficial:

```powershell
./scripts/build/build_clean_architecture.ps1
```
No Linux, gere o `.exe` pelo workflow de CI que roda em ambiente Windows.

## DocumentaÃ§Ã£o

Use o README principal como ponto de entrada e deixe os detalhes nos guias especÃ­ficos. A pasta `docs/` fica reservada para estrutura principal e guides; documentaÃ§Ã£o de novas features deve ir em `docs/features/`.

- [Ãndice da documentaÃ§Ã£o](docs/README.md)
- [Governanca de IA e instrucoes canonicas](docs/ai/README.md)
- [Guia de build do executÃ¡vel Windows](docs/BUILD_GUIDE.md)
- [Arquitetura do projeto](docs/ARCHITECTURE.md)
- [Guia do Desktop App](docs/README_DESKTOP_APP.md)
- [ConfiguraÃ§Ã£o de hotkeys](docs/HOTKEY_SETUP.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## ObservaÃ§Ãµes

- NÃ£o versione o `DISCORD_TOKEN`
- O bot e o Desktop App devem continuar funcionando de forma independente
- Prefira consultar `docs/` para detalhes de arquitetura, setup e troubleshooting

