# Setup do Ambiente

Este projeto usa um ambiente virtual Python (`.venv`) como parte do fluxo de instalacao e desenvolvimento.

## Requisitos

- Python 3.11 ou superior
- `ffmpeg` para o fluxo de voz do Discord

## 1. Criar o `.venv`

No diretorio raiz do repositorio:

### Windows PowerShell

```powershell
python -m venv .venv
```

### Linux/macOS

```bash
python3 -m venv .venv
```

## 2. Ativar o `.venv`

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear scripts locais, rode esta permissao uma vez no usuario atual:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Linux/macOS

```bash
source .venv/bin/activate
```

## 3. Instalar dependencias

Com o `.venv` ativo:

```bash
pip install -r requirements.txt
```

## 4. Instalar o FFmpeg no Windows para voz do Discord

No Windows, o fluxo de voz do Discord tambem precisa do `FFmpeg` disponivel no `PATH`.

Uma forma simples de instalar localmente:

```powershell
winget install ffmpeg
```

Depois da instalacao, abra um novo terminal e confirme:

```powershell
ffmpeg -version
```

## 5. Dependencia opcional para voz no Discord

Em alguns ambientes, o fluxo de voz do Discord pode precisar de `PyNaCl`:

```bash
pip install pynacl
```

## 6. Validar o ambiente

Confira se o terminal esta usando o Python do ambiente virtual:

```bash
python --version
pip --version
```

O caminho mostrado por `pip --version` deve apontar para `.venv`.

Para o bot do Discord com voz, confirme tambem que `ffmpeg -version` funciona no mesmo terminal em que o bot sera executado.

## 6.1. Storage local do bot

Por padrão, o bot local usa storage JSON:

```env
CONFIG_STORAGE_BACKEND=json
CONFIG_STORAGE_DIR=configs
```

Se quiser testar o mesmo backend de persistência usado em produção, suba apenas
o Postgres com Docker:

```bash
docker compose -f docker-compose.postgres.yml up -d
```

Depois configure o `.env` com:

```env
CONFIG_STORAGE_BACKEND=postgres
DATABASE_URL=postgresql://tts_user:change_me@127.0.0.1:5432/tts_hotkey_windows
POSTGRES_DB=tts_hotkey_windows
POSTGRES_USER=tts_user
POSTGRES_PASSWORD=change_me
POSTGRES_PORT=5432
```

Se quiser voltar para storage local em arquivos, pare o Postgres se não for mais
usar e retorne `CONFIG_STORAGE_BACKEND=json`.

## 6.2. Redis opcional para a fila do bot

Se quiser usar a fila Redis do bot localmente, suba apenas o Redis com Docker:

```bash
docker compose -f docker-compose.redis.yml up -d
```

Depois configure o `.env` com:

```env
TTS_QUEUE_BACKEND=redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_KEY_PREFIX=tts
REDIS_COMPLETED_ITEM_TTL_SECONDS=900
```

Se nao quiser Redis, mantenha `TTS_QUEUE_BACKEND=inmemory`.

## 6.3. Stack completa de produção local

Para validar o stack completo com bot, Postgres, Redis e observabilidade, use:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

O `docker-compose.prod.yml` tambem aceita versionamento da imagem do bot via
`BOT_IMAGE` e `APP_VERSION`. Em producao, publique uma imagem com tag imutavel e
suba com essa versao registrada no `.env.prod`; para rollback, volte o
`APP_VERSION` para a ultima versao boa.

Para desenvolvimento diário, prefira escolher somente as dependências que você
precisa: `docker-compose.postgres.yml` para Postgres e
`docker-compose.redis.yml` para Redis.

## 7. Desativar quando terminar

```bash
deactivate
```

## Observacoes

- Sempre ative o `.venv` antes de rodar `pip install`, `pytest`, `python -m src.bot` ou `python app.py`.
- No Windows, instalar apenas o pacote Python nao basta para voz no Discord: o `FFmpeg` precisa estar instalado no sistema e acessivel no `PATH`.
- O bot do Discord e o Desktop App continuam com entrypoints separados, mas usam o mesmo ambiente virtual durante o desenvolvimento.
