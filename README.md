# python-tts-discord-bot

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7ed90fe1cc6f4090a7386df4681df463)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/7ed90fe1cc6f4090a7386df4681df463)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

Projeto com dois aplicativos independentes:

- Bot do Discord para entrar em canal de voz e reproduzir TTS
- App standalone com hotkeys para capturar texto e enviar ao bot

O repositório segue Clean Architecture e busca reutilizar lógica entre os dois fluxos, sem duplicação entre `standalone` e `src`.

## Estrutura rápida

- `main.py`: sobe o bot do Discord e o servidor HTTP
- `app.py`: inicia o app standalone/hotkey
- `src/`: camadas principais da aplicação
- `docs/`: documentação complementar
- `BUILD_GUIDE.md`: guia de build do executável Windows

## Requisitos

- Python 3.11+
- `ffmpeg` para o fluxo de voz do Discord
- Ambiente virtual recomendado

Instalação básica:

```bash
pip install -r requirements.txt
```

Para voz no Discord localmente, também pode ser necessário:

```bash
pip install pynacl
```

## Execução rápida

Configure um arquivo `.env` com pelo menos:

```env
DISCORD_TOKEN=seu_token_aqui
DISCORD_BOT_URL=http://127.0.0.1:5000
```

Suba o bot:

```bash
python main.py
```

Em outro terminal, rode o app standalone:

```bash
python app.py
```

## Testes

```bash
pytest
```

## Documentação

Use o README principal como ponto de entrada e deixe os detalhes nos guias específicos:

- [Índice da documentação](docs/README.md)
- [Guia de build do executável Windows](BUILD_GUIDE.md)
- [Arquitetura do projeto](docs/ARCHITECTURE.md)
- [Guia do app standalone](docs/README_STANDALONE.md)
- [Configuração de hotkeys](docs/HOTKEY_SETUP.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Observações

- Não versione o `DISCORD_TOKEN`
- O bot e o app standalone devem continuar funcionando de forma independente
- Prefira consultar `docs/` para detalhes de arquitetura, setup e troubleshooting
