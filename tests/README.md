# Testes

Este diretório reúne os testes automatizados do projeto.

## Ambiente

O ambiente local de testes usa `.env` como fonte de variáveis.

- alguns testes e defaults do Desktop App dependem de valores carregados do arquivo `.env`
- ao reproduzir falhas localmente, confira se o `.env` está presente e coerente com o cenário esperado
- quando um teste sobrescreve variáveis com `monkeypatch`, isso vale apenas para aquele teste

## Execução

```powershell
pip install -r requirements-test.txt
python -m pytest
```

### Desktop App no `.venv`

Para rodar a suíte do Desktop App usando o ambiente virtual local:

```powershell
.venv\Scripts\python -m pytest tests/unit/standalone -q
```

## Estrutura

- `tests/unit/`: testes unitários por camada
- `tests/unit/standalone/`: testes do runtime interno do Desktop App
- `tests/conftest.py`: fixtures e helpers compartilhados
