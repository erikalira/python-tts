# Testes Unitários - TTS Hotkey Windows

## 📋 Estrutura de Testes

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures e mocks compartilhados
├── unit/
│   ├── core/
│   │   └── test_entities.py       # Testes de entidades
│   ├── application/
│   │   └── test_use_cases.py      # Testes de casos de uso
│   ├── infrastructure/
│   │   ├── test_tts_engines.py    # Testes de engines TTS
│   │   └── test_config_repository.py
│   └── presentation/
│       └── test_http_controllers.py
```

## 🚀 Executando os Testes

### Instalar dependências de teste
```powershell
pip install -r requirements-test.txt
```

### Executar todos os testes
```powershell
pytest
```

### Executar apenas testes rápidos (sem integração lenta)
```powershell
pytest -m "not slow"
```

### Executar com relatório HTML de cobertura
```powershell
pytest --cov-report=html
```

### Executar testes específicos
```powershell
# Apenas testes unitários
pytest tests/unit/

# Apenas uma classe de teste
pytest tests/unit/core/test_entities.py::TestTTSRequest

# Apenas um teste específico
pytest tests/unit/application/test_use_cases.py::TestSpeakTextUseCase::test_execute_success
```

### Executar testes com marcadores
```powershell
# Apenas testes rápidos (excluir testes lentos)
pytest -m "not slow"

# Apenas testes de integração
pytest -m integration

# Apenas testes que não precisam de rede
pytest -m "not network"
```

## 📊 Cobertura de Testes

Após executar `pytest`, abra o relatório HTML:
```powershell
.\htmlcov\index.html
```

**Meta de cobertura:** 68%+ (configurado em `pytest.ini`)  
**Cobertura atual:** 76% (62 testes - 61 passando, 1 skipped)

## ✅ O que está sendo testado

### Core Layer (Domain)
- ✅ `TTSRequest`: Criação com todos os campos, apenas texto
- ✅ `TTSConfig`: Valores padrão, valores customizados
- ✅ `AudioFile`: Criação, cleanup

### Application Layer
- ✅ `SpeakTextUseCase`:
  - Execução bem-sucedida
  - Texto faltando
  - Canal não encontrado
  - Busca por channel_id, member_id, guild_id
- ✅ `ConfigureTTSUseCase`:
  - Obter configuração atual
  - Atualizar engine, language, voice_id
  - Engine inválido
  - Múltiplas configurações

### Infrastructure Layer
- ✅ `TTSEngineFactory`: Criar engines (gtts, pyttsx3, inválido)
- ✅ `InMemoryConfigRepository`:
  - Config padrão
  - Config por guild
  - Múltiplas guilds
  - Isolamento de configs

### Presentation Layer
- ✅ `SpeakController`:
  - Requisição válida
  - Texto faltando
  - JSON inválido

## 🧪 Mocks e Fixtures

### Fixtures Disponíveis (conftest.py)
- `mock_tts_engine`: Mock de ITTSEngine
- `mock_voice_channel`: Mock de IVoiceChannel
- `mock_channel_repository`: Mock de IVoiceChannelRepository
- `mock_config_repository`: Mock de IConfigRepository
- `sample_tts_request`: Exemplo de TTSRequest
- `sample_tts_config`: Exemplo de TTSConfig

### Usando Fixtures
```python
def test_example(mock_tts_engine, sample_tts_request):
    # Usar fixtures nos testes
    assert mock_tts_engine is not None
    assert sample_tts_request.text == "Hello world"
```

## 📝 Escrevendo Novos Testes

### Template de Teste
```python
import pytest
from src.module import ClassToTest

class TestClassName:
    """Test ClassToTest."""
    
    def test_method_success(self):
        """Test successful execution."""
        # Arrange
        instance = ClassToTest()
        
        # Act
        result = instance.method()
        
        # Assert
        assert result is not None
    
    def test_method_error(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            instance = ClassToTest()
            instance.method(invalid_param)
```

### Teste Assíncrono
```python
@pytest.mark.asyncio
async def test_async_method(mock_dependency):
    """Test async method."""
    result = await async_function(mock_dependency)
    assert result["success"] is True
```

## 🎯 Benefícios dos Testes

### Garantia de Qualidade
- ✅ Detecta bugs antes do deploy
- ✅ Garante que mudanças não quebram funcionalidades existentes
- ✅ Documenta comportamento esperado

### Refatoração Segura
- ✅ Permite refatorar com confiança
- ✅ Testes passam = código funciona
- ✅ CI/CD pode bloquear merges com testes falhando

### Design Melhor
- ✅ Código testável = código bem estruturado
- ✅ Interfaces claras (mocks fáceis)
- ✅ Baixo acoplamento

## 🔄 CI/CD Integration

### GitHub Actions Exemplo
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install -r requirements.txt -r requirements-test.txt
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## 📈 Próximos Passos

1. ✅ Adicionar testes de integração
2. ✅ Configurar CI/CD com GitHub Actions
3. ✅ Aumentar cobertura para 80%+
4. ✅ Adicionar testes de performance
5. ✅ Testes end-to-end com Docker

## 🐛 Troubleshooting

### Erro: ModuleNotFoundError
```powershell
# Instalar em modo development
pip install -e .
```

### Testes lentos
```powershell
# Executar em paralelo
pip install pytest-xdist
pytest -n auto
```

### Coverage não funciona
```powershell
# Reinstalar pytest-cov
pip install --upgrade pytest-cov
```
