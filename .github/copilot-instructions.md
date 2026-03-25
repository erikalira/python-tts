# GitHub Copilot Instructions

## Project Context

Este é um projeto Python de Text-to-Speech (TTS) que integra com Discord e Flask, com suporte completo a aplicações standalone. O projeto implementa Clean Architecture e SOLID principles tanto na versão Discord quanto na versão standalone configurável com interface gráfica.

## Architecture Overview

- **Clean Architecture**: Separação clara entre camadas (core, application, infrastructure, presentation)
- **Domain-Driven Design**: Entidades e casos de uso bem definidos
- **Dependency Injection**: Uso do padrão para melhor testabilidade
- **SOLID Principles**: Especialmente Single Responsibility e Dependency Inversion

## Project Structure

```
src/
├── core/           # Entidades e regras de negócio
│   ├── entities.py
│   └── interfaces.py
├── application/    # Casos de uso da aplicação
│   └── use_cases.py
├── infrastructure/ # Implementações concretas (Discord, TTS, HTTP)
│   ├── discord/
│   ├── tts/
│   └── http/
├── presentation/   # Controllers e comandos
│   ├── discord_commands.py
│   └── http_controllers.py
└── standalone/     # NOVA: Versão standalone com Clean Architecture
    ├── config/     # Configuração standalone com dataclasses
    │   └── standalone_config.py
    ├── app/        # Aplicação principal standalone
    │   └── simple_app.py
    ├── services/   # Serviços específicos standalone
    │   ├── tts_services.py
    │   ├── hotkey_services.py
    │   └── notification_services.py
    └── gui/        # Interface gráfica
        └── simple_gui.py

config/             # Configuração e DI Container (Discord/Flask)
├── settings.py     # Variáveis de ambiente e configurações
└── container.py    # Dependency Injection Container

scripts/build/      # Scripts de build para Windows
├── build_clean_architecture.ps1  # Build Clean Architecture (recomendado)

docs/               # Documentação técnica detalhada
├── ARCHITECTURE.md          # Arquitetura e design do sistema
├── README_STANDALONE.md     # Versão standalone do aplicativo
├── TROUBLESHOOTING.md       # Guia de solução de problemas
├── HOTKEY_SETUP.md         # Configuração de hotkeys
└── SISTEMA_CONEXAO_INTELIGENTE.md  # Sistema de conexão Discord
```

## Code Style Guidelines

### Python Standards

- **PEP 8**: Siga rigorosamente as convenções de formatação
- **Type Hints**: Use em todas as funções, métodos e variáveis
- **Docstrings**: Formato Google para documentação
- **pathlib.Path**: Prefira para manipulação de caminhos em vez de os.path

### Naming Conventions

- **Classes**: PascalCase (ex: `TTSConfig`, `VoiceChannel`)
- **Functions/Methods**: snake_case (ex: `validate_config`, `send_message`)
- **Constants**: UPPER_SNAKE_CASE (ex: `DEFAULT_RATE`, `MAX_RETRIES`)
- **Files**: snake_case (ex: `voice_channel.py`, `use_cases.py`)
- **Private members**: Prefixo underscore (ex: `_internal_method`)

### Code Organization

- **Single Responsibility**: Uma classe/função deve ter apenas um motivo para mudar
- **Small Functions**: Máximo 20-30 linhas, uma responsabilidade
- **Meaningful Names**: Nomes descritivos que explicam a intenção
- **Avoid Deep Nesting**: Máximo 3 níveis de indentação

## Dependencies & Technologies

### Core Libraries

- **Discord.py**: Bot do Discord e integração de voz
- **Flask**: API web e endpoints HTTP
- **gTTS & pyttsx3**: Engines de text-to-speech
- **python-dotenv**: Gerenciamento de variáveis de ambiente

### Development Tools

- **pytest**: Framework de testes
- **pytest-asyncio**: Suporte a testes assíncronos
- **python-dotenv**: Configuração via .env

## Configuration Management

- **Environment Variables**: Use para configurações sensíveis e ambiente-específicas
- **Config Class**: Centralize configurações em `config/settings.py`
- **Validation**: Sempre valide configurações no startup
- **Defaults**: Forneça valores padrão sensatos

### Required Environment Variables

```
DISCORD_TOKEN=your_bot_token
TTS_ENGINE=gtts|pyttsx3
TTS_LANGUAGE=pt
TTS_VOICE_ID=roa/pt-br
TTS_RATE=180
PORT=8080
```

## Error Handling Patterns

### Exception Hierarchy

- **Custom Exceptions**: Crie exceções específicas do domínio
- **Meaningful Messages**: Mensagens de erro claras e acionáveis
- **Logging**: Use logging adequado para debugging
- **Graceful Degradation**: Sistema deve continuar funcionando quando possível

### Example Pattern

```python
class TTSError(Exception):
    """Base exception for TTS operations."""
    pass

class EngineNotAvailableError(TTSError):
    """Raised when TTS engine is not available."""
    pass
```

## Testing Guidelines

### Test Structure

- **Unit Tests**: Para lógica de negócio e casos de uso
- **Integration Tests**: Para componentes externos (Discord, TTS)
- **Test Doubles**: Use mocks para dependências externas
- **Arrange-Act-Assert**: Estrutura clara dos testes

### Test Naming

```python
def test_should_validate_config_when_all_required_fields_present():
    """Test method names should describe the scenario and expected outcome."""
    pass
```

### Coverage Goals

- **High Coverage**: Mantenha > 80% de cobertura
- **Critical Paths**: 100% cobertura para funcionalidades críticas
- **Edge Cases**: Teste cenários de erro e limites

## Async/Await Patterns

### Discord Integration

- **Async Methods**: Use para operações Discord
- **Context Managers**: Para recursos que precisam cleanup
- **Error Handling**: Proper exception handling em async code

### Example

```python
async def send_tts_message(self, text: str) -> bool:
    """Send TTS message to voice channel."""
    try:
        audio_data = await self.tts_service.generate(text)
        await self.voice_client.play(audio_data)
        return True
    except TTSError as e:
        logger.error(f"TTS generation failed: {e}")
        return False
```

## Performance Considerations

- **Async I/O**: Para operações de rede e arquivo
- **Caching**: Implemente cache para operações custosas
- **Memory Management**: Libere recursos adequadamente
- **Rate Limiting**: Respeite limites de APIs externas

## Security Guidelines

- **Environment Variables**: Nunca hardcode tokens/secrets
- **Input Validation**: Valide todos os inputs externos
- **Sanitization**: Sanitize dados antes de usar
- **Least Privilege**: Dê apenas as permissões necessárias

## Discord Bot Specific

- **Command Patterns**: Use decorators para comandos
- **Event Handling**: Separe lógica de eventos
- **Voice Channels**: Gerencie conexões adequadamente
- **Permissions**: Verifique permissões antes de ações

## TTS Integration

- **Engine Abstraction**: Use interface comum para diferentes engines
- **Fallback Strategy**: Implemente fallback entre engines
- **Audio Quality**: Balance qualidade vs. performance
- **Language Support**: Suporte múltiplos idiomas quando possível

## Logging & Monitoring

- **Structured Logging**: Use logging estruturado
- **Log Levels**: Appropriate levels (DEBUG, INFO, WARNING, ERROR)
- **No Sensitive Data**: Nunca logue tokens ou dados sensíveis
- **Performance Metrics**: Log tempos de operações críticas

## Common Patterns to Follow

### Dependency Injection

```python
def __init__(self, tts_service: TTSService, config: Config):
    self._tts_service = tts_service
    self._config = config
```

### Factory Pattern

```python
def create_tts_engine(engine_type: str) -> TTSEngine:
    """Factory for TTS engines."""
    if engine_type == 'gtts':
        return GTTSEngine()
    elif engine_type == 'pyttsx3':
        return Pyttsx3Engine()
    raise ValueError(f"Unknown engine: {engine_type}")
```

### Repository Pattern

```python
class ConfigRepository(ABC):
    """Abstract repository for configuration."""

    @abstractmethod
    def load_config(self) -> Config:
        """Load configuration."""
        pass
```

## Code Quality Checklist

- [ ] Type hints em todas as funções
- [ ] Docstrings para classes e métodos públicos
- [ ] Testes unitários para nova funcionalidade
- [ ] Validação de inputs
- [ ] Error handling adequado
- [ ] Logging apropriado
- [ ] Performance considerations
- [ ] Security best practices
- [ ] Documentação atualizada em docs/ se necessário

## Documentation Guidelines

### Documentation Structure

- **README.md**: Overview do projeto, instalação e uso básico
- **docs/ARCHITECTURE.md**: Arquitetura detalhada e decisões de design
- **docs/TROUBLESHOOTING.md**: Guia de solução de problemas comuns
- **docs/README_STANDALONE.md**: Versão standalone e configurações específicas
- **docs/HOTKEY_SETUP.md**: Configuração de hotkeys e atalhos
- **docs/SISTEMA_CONEXAO_INTELIGENTE.md**: Sistema de conexão Discord
- **Docstrings**: Formato Google em todas as classes e métodos públicos

### When Adding New Features

- Documente casos de uso complexos em `docs/`
- Só adicione documentação no docs/ ou no readme.md
- Atualize o README.md se adicionar novos comandos ou funcionalidades
- Inclua exemplos de código em docstrings quando apropriado
- Documente configurações de ambiente em `docs/TROUBLESHOOTING.md`
- Mantenha a documentação de arquitetura atualizada

### Code Documentation Standards

```python
def process_tts_request(text: str, engine: str = "gtts") -> AudioData:
    """Process text-to-speech request with specified engine.

    Args:
        text: Text to be converted to speech
        engine: TTS engine to use (gtts or pyttsx3)

    Returns:
        AudioData object containing the generated audio

    Raises:
        TTSError: If TTS generation fails
        EngineNotAvailableError: If specified engine is not available

    Example:
        >>> audio = process_tts_request("Hello world", "gtts")
        >>> audio.play()
    """
    pass
```

## Standalone Application Architecture

### Core Components

- **StandaloneConfig**: Dataclass-based configuration with validation
- **SimpleApplication**: Main application orchestrating all services
- **Service Layer**: TTSProcessor, HotkeyManager, SystemTrayService
- **GUI Layer**: Tkinter-based configuration interface
- **Repository Pattern**: Configuration persistence with JSON

### Entry Points

- **tts_hotkey_configurable.py**: Main entry point with clean architecture and embedded fallback
- **Build Scripts**: PowerShell scripts for Windows executable creation
- **Platform Compatibility**: Windows (full features) and Linux (graceful degradation)

### Key Features

- **Clean Architecture**: Full separation of concerns across layers
- **SOLID Principles**: Dependency injection, single responsibility
- **Configuration Management**: Persistent settings with GUI configuration
- **Multi-Engine TTS**: gTTS and pyttsx3 support with fallback
- **System Integration**: Global hotkeys, system tray, notifications
- **Robust Error Handling**: Graceful degradation and fallback mechanisms

## When Writing New Code

1. **Understand the Domain**: Leia `docs/ARCHITECTURE.md` e código existente primeiro
2. **Follow Patterns**: Use os padrões estabelecidos na arquitetura Clean (tanto Discord quanto standalone)
3. **Test First**: Considere TDD quando apropriado
4. **Platform Compatibility**: Considere Windows (target) e Linux (development) environments
5. **Documentation**: Documente APIs públicas e atualize `docs/` conforme necessário
6. **Review**: Considere o impacto nas outras camadas e na documentação existente
