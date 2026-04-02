# Arquitetura do Projeto - TTS Hotkey Windows

## Visão Geral

Este projeto contém dois aplicativos independentes:

1. Bot do Discord com endpoint HTTP para TTS
2. Desktop app Windows com hotkeys, GUI e system tray

Ambos seguem Clean Architecture e os princípios SOLID para garantir:

- código modular e testável
- baixo acoplamento entre camadas
- alta coesão dentro dos módulos
- facilidade de manutenção e extensão
- independência de frameworks externos
- separação clara de responsabilidades
- dependency injection nas bordas do sistema

## Estado atual dos entry points

### Desktop app

- Entry point oficial: `app.py`
- Implementação principal: `src/standalone/`

### Bot Discord

- Entry point oficial: `src/bot.py`
- Servidor HTTP operacional: `src/infrastructure/http/server.py`

O bot agora usa um único runtime operacional baseado em `src/bot.py` com `aiohttp`.

## Estrutura de Diretórios

```
tts-hotkey-windows/
├── config/                    # Configuração e dependency injection do bot
│   ├── __init__.py
│   ├── settings.py            # Carregamento de variáveis de ambiente
│   └── container.py           # DI container
│
├── src/
│   ├── core/                  # Camada de domínio
│   │   ├── __init__.py
│   │   ├── entities.py        # Entidades de negócio
│   │   └── interfaces.py      # Interfaces e contratos
│   │
│   ├── application/           # Camada de aplicação
│   │   ├── __init__.py
│   │   └── use_cases.py       # Casos de uso
│   │
│   ├── infrastructure/        # Camada de infraestrutura
│   │   ├── __init__.py
│   │   ├── tts/               # Implementações de TTS
│   │   │   ├── __init__.py
│   │   │   ├── engines.py
│   │   │   └── config_repository.py
│   │   │
│   │   ├── discord/           # Implementações Discord
│   │   │   ├── __init__.py
│   │   │   └── voice_channel.py
│   │   │
│   │   ├── http/              # Servidor HTTP modular atual
│   │   │   ├── __init__.py
│   │   │   └── server.py      # HTTPServer (aiohttp)
│   │
│   ├── presentation/          # Camada de apresentação
│   │   ├── __init__.py
│   │   ├── discord_commands.py
│   │   └── http_controllers.py
│   │
│   ├── bot.py                 # Entry point do bot
│   │
│   └── standalone/            # Runtime standalone
│       ├── __init__.py
│       │
│       ├── config/            # Configuração com dataclasses
│       │   ├── __init__.py
│       │   └── standalone_config.py
│       │
│       ├── app/               # Aplicação principal
│       │   ├── __init__.py
│       │   └── standalone_app.py
│       │
│       ├── services/          # Serviços do standalone
│       │   ├── __init__.py
│       │   ├── tts_services.py
│       │   ├── hotkey_services.py
│       │   └── notification_services.py
│       │
│       └── gui/               # Interface gráfica
│           ├── __init__.py
│           ├── simple_gui.py
│           └── configuration_gui.py
│
├── app.py                     # Entry point do standalone
├── scripts/build/
│   └── build_clean_architecture.ps1
│
├── tests/
│   ├── unit/
│   │   ├── core/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   ├── presentation/
│   │   └── standalone/
│   ├── conftest.py
│   └── README.md
│
├── .env
├── requirements.txt
├── requirements-test.txt
├── pytest.ini
├── Dockerfile
└── README.md
```

## 🎯 Arquitetura Standalone (Clean Architecture)

A versão standalone implementa Clean Architecture completa com as seguintes camadas:

### 🔧 **Config Layer** (`src/standalone/config/`)

```python
@dataclass
class StandaloneConfig:
    """Configuração principal com validação integrada."""
    tts: TTSConfig
    discord: DiscordConfig
    hotkey: HotkeyConfig
    interface: InterfaceConfig
    network: NetworkConfig

    @classmethod
    def create_default(cls) -> 'StandaloneConfig':
        """Factory method com configurações padrão."""

class ConfigurationRepository:
    """Repository pattern para persistência de configuração."""
    def load(self) -> StandaloneConfig
    def save(self, config: StandaloneConfig) -> None
```

### 🎯 **Service Layer** (`src/standalone/services/`)

```python
class TTSProcessor:
    """Processamento de TTS com múltiplos engines."""
    def __init__(self, config: StandaloneConfig)
    def process_text(self, text: str) -> bool

class HotkeyManager:
    """Gerenciamento de hotkeys globais."""
    def __init__(self, config: StandaloneConfig)
    def start_listening(self) -> None

class SystemTrayService:
    """Sistema de notificações e system tray."""
    def __init__(self, config: StandaloneConfig)
    def run_tray(self) -> None
```

### 🟢 **Application Layer** (`src/standalone/app/`)

```python
class StandaloneApplication:
    """Orquestrador principal da aplicação."""
    def __init__(self)
    def initialize(self) -> bool
    def run(self) -> None

    # Coordena configuração, TTS, hotkeys e tray
    _config_repository: ConfigurationRepository
    _config_service: ConfigurationService
    _tts_processor: TTSProcessor
    _hotkey_manager: HotkeyManager
    _notification_service: SystemTrayService
```

### 🔴 **Interface Layer** (`src/standalone/gui/`)

```python
class ConfigurationService:
    """Orquestra a configuração inicial e a reconfiguração do app."""
    def __init__(self, prefer_gui: bool = True)
    def get_configuration(self, config: StandaloneConfig) -> StandaloneConfig | None

class GUIConfigurationInterface:
    """Interface gráfica para editar a configuração."""
    def show_configuration_dialog(
        self,
        current_config: StandaloneConfig
    ) -> StandaloneConfig | None
```

### 🚀 **Entry Point** (`app.py`)

```python
from src.standalone.app.standalone_app import main


if __name__ == "__main__":
    main()
```

## 🎯 Princípios SOLID Aplicados

### 1. **S**ingle Responsibility Principle (SRP)

Cada classe tem uma única responsabilidade:

- `GTTSEngine`: Apenas gera áudio com gTTS
- `SpeakTextUseCase`: Apenas orquestra a lógica de falar texto
- `SpeakController`: Apenas trata requisições HTTP
- `DiscordCommands`: Apenas trata comandos Discord

### 2. **O**pen/Closed Principle (OCP)

Extensível sem modificar código existente:

- `TTSEngineFactory`: Fácil adicionar novos engines TTS
- `IVoiceChannel`: Pode implementar para outras plataformas além do Discord
- Novos casos de uso podem ser adicionados sem modificar existentes

### 3. **L**iskov Substitution Principle (LSP)

Implementações podem ser substituídas por suas abstrações:

- Qualquer `ITTSEngine` funciona no `SpeakTextUseCase`
- Qualquer `IVoiceChannel` pode ser usado
- Fácil criar mocks para testes

### 4. **I**nterface Segregation Principle (ISP)

Interfaces pequenas e específicas:

- `ITTSEngine`: Apenas gera áudio
- `IVoiceChannel`: Apenas operações de canal de voz
- `IConfigRepository`: Apenas gerencia configuração
- Nenhuma classe é forçada a implementar métodos desnecessários

### 5. **D**ependency Inversion Principle (DIP)

Dependências apontam para abstrações:

- `SpeakTextUseCase` depende de `ITTSEngine` (interface), não de `GTTSEngine` (implementação)
- `Container` injeta dependências concretas
- Fácil trocar implementações sem modificar código

## 📊 Fluxo de Dados (Clean Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  (Controllers, Discord Commands, HTTP Endpoints)            │
│  • SpeakController                                          │
│  • DiscordCommands                                          │
└────────────────────┬────────────────────────────────────────┘
                     │ Chama
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│  (Use Cases - Regras de Negócio)                           │
│  • SpeakTextUseCase                                         │
│  • ConfigureTTSUseCase                                      │
└────────────────────┬────────────────────────────────────────┘
                     │ Usa
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      CORE LAYER                              │
│  (Entities & Interfaces - Sem dependências externas)        │
│  • TTSRequest, TTSConfig, AudioFile                         │
│  • ITTSEngine, IVoiceChannel, IConfigRepository            │
└─────────────────────────────────────────────────────────────┘
                     ▲
                     │ Implementa
                     │
┌─────────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                         │
│  (Implementações Concretas)                                 │
│  • GTTSEngine, Pyttsx3Engine                                │
│  • DiscordVoiceChannel                                      │
│  • InMemoryConfigRepository                                 │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Dependency Injection Container

O `Container` em `config/container.py` é responsável por:

1. **Criar todas as dependências** (repositórios, engines, use cases)
2. **Injetar dependências** nos componentes que precisam
3. **Configurar o Discord client** e registrar eventos
4. **Centralizar a construção** do grafo de objetos

```python
# Exemplo de uso:
config = Config()
container = Container(config)

# Todas as dependências já estão configuradas:
# - container.speak_use_case
# - container.config_use_case
# - container.discord_client
# - container.speak_controller
```

## Como Executar

### Desenvolvimento Local

```bash
# Bot do Discord com runtime atual
python -m src.bot

# Standalone Windows / hotkey
python app.py
```

### Desenvolvimento Local (Docker)

```bash
# 0. Iniciar Docker Desktop (se não estiver rodando)
# Windows PowerShell:
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Aguardar alguns segundos até Docker iniciar, então verificar:
docker ps  # Deve retornar sem erro

# 1. Build da imagem
docker build -t tts-hotkey .

# 2. Executar container
docker run -p 10000:10000 --env-file .env tts-hotkey

# 3. Parar o container
docker ps  # Ver containers rodando
docker stop <container_id>

# 4. Ver logs
docker logs <container_id>

# 5. Remover container
docker rm <container_id>

# 6. Remover imagem
docker rmi tts-hotkey
```

**Comandos úteis Docker:**

```bash
# Ver containers rodando
docker ps

# Ver todos os containers (incluindo parados)
docker ps -a

# Ver imagens
docker images

# Executar em modo interativo (ver logs em tempo real)
docker run -it -p 10000:10000 --env-file .env tts-hotkey

# Executar em background (detached)
### Docker (Desenvolvimento e Testes)

# Build image
docker build -t tts-hotkey .

# Rodar container
docker run -d -p 10000:10000 --env-file .env tts-hotkey

# Limpar tudo
docker system prune -a
```

## 🧪 Testabilidade

Exemplos de testes possíveis:

```python
# Mock TTS Engine
class MockTTSEngine(ITTSEngine):
    async def generate_audio(self, text, config):
        return AudioFile(path="/fake/path.wav")

# Mock Voice Channel
class MockVoiceChannel(IVoiceChannel):
    def __init__(self):
        self.played_audio = []

    async def play_audio(self, audio):
        self.played_audio.append(audio.path)

# Testar use case isoladamente
def test_speak_use_case():
    mock_engine = MockTTSEngine()
    mock_channel = MockVoiceChannel()
    mock_repo = MockChannelRepository(mock_channel)
    mock_config = MockConfigRepository()
    audio_queue = InMemoryAudioQueue()

    use_case = SpeakTextUseCase(
        mock_engine,
        mock_repo,
        mock_config,
        audio_queue,
    )
    result = await use_case.execute(TTSRequest(text="test"))

    assert result["success"] == True
    assert len(mock_channel.played_audio) == 1
```

## 🧪 Testes Unitários

O projeto possui uma suíte completa de testes.

### Executar testes:

```powershell
# Todos os testes
pytest

# Testes rápidos (sem integração lenta)
pytest -m "not slow"

# Com relatório HTML
pytest --cov-report=html
```

Veja `tests/README.md` para mais detalhes.

## 🎓 Referências

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Dependency Injection in Python](https://python-dependency-injector.ets-labs.org/)
