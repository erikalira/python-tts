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

## 4. Dependencia opcional para voz no Discord

Em alguns ambientes, o fluxo de voz do Discord pode precisar de `PyNaCl`:

```bash
pip install pynacl
```

## 5. Validar o ambiente

Confira se o terminal esta usando o Python do ambiente virtual:

```bash
python --version
pip --version
```

O caminho mostrado por `pip --version` deve apontar para `.venv`.

## 6. Desativar quando terminar

```bash
deactivate
```

## Observacoes

- Sempre ative o `.venv` antes de rodar `pip install`, `pytest`, `python -m src.bot` ou `python app.py`.
- O bot do Discord e o Desktop App continuam com entrypoints separados, mas usam o mesmo ambiente virtual durante o desenvolvimento.
