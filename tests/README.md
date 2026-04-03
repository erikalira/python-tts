# Testes

Este diretÃ³rio reÃºne os testes automatizados do projeto.

## Ambiente

O ambiente local de testes usa `.env` como fonte de variÃ¡veis.

- alguns testes e defaults do Desktop App dependem de valores carregados do arquivo `.env`
- ao reproduzir falhas localmente, confira se o `.env` estÃ¡ presente e coerente com o cenÃ¡rio esperado
- quando um teste sobrescreve variÃ¡veis com `monkeypatch`, isso vale apenas para aquele teste

## ExecuÃ§Ã£o

```powershell
pip install -r requirements-test.txt
python -m pytest
```

### Desktop App no `.venv`

Para rodar a suÃ­te do Desktop App usando o ambiente virtual local:

```powershell
.venv\Scripts\python -m pytest tests/unit/desktop -q
```

## Estrutura

- `tests/unit/`: testes unitÃ¡rios por camada
- `tests/unit/desktop/`: testes do runtime interno do Desktop App
- `tests/conftest.py`: fixtures e helpers compartilhados

