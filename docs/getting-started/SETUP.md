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

## 7. Desativar quando terminar

```bash
deactivate
```

## Observacoes

- Sempre ative o `.venv` antes de rodar `pip install`, `pytest`, `python -m src.bot` ou `python app.py`.
- No Windows, instalar apenas o pacote Python nao basta para voz no Discord: o `FFmpeg` precisa estar instalado no sistema e acessivel no `PATH`.
- O bot do Discord e o Desktop App continuam com entrypoints separados, mas usam o mesmo ambiente virtual durante o desenvolvimento.
