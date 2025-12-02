# Arquitetura do Projeto - TTS Hotkey Windows

## 📐 Visão Geral

Este projeto implementa **duas arquiteturas complementares**:

**1. Clean Architecture para Discord/Flask** - Versão completa com bot e servidor web  
**2. Clean Architecture para Standalone** - Versão desktop com GUI e system tray

Ambas seguem **Clean Architecture** e os princípios **SOLID** para garantir:

- ✅ Código modular e testável
- ✅ Baixo acoplamento entre camadas
- ✅ Alta coesão dentro dos módulos
- ✅ Facilidade de manutenção e extensão
- ✅ Independência de frameworks externos
- ✅ Separação clara de responsabilidades
- ✅ Dependency Injection em todas as camadas

## 🏗️ Estrutura de Diretórios

```
tts-hotkey-windows/
├── config/                    # 🔧 DISCORD/FLASK: Configuração e Dependency Injection
│   ├── __init__.py
│   ├── settings.py           # Carregamento de variáveis de ambiente
│   └── container.py          # DI Container (Injeção de Dependências)
│
├── src/
│   ├── core/                 # 🔵 CAMADA DE DOMÍNIO (Domain Layer)
│   │   ├── __init__.py
│   │   ├── entities.py       # Entidades de negócio (TTSRequest, TTSConfig, AudioFile)
│   │   └── interfaces.py     # Interfaces/Contratos (ITTSEngine, IVoiceChannel, etc)
│   │
│   ├── application/          # 🟢 CAMADA DE APLICAÇÃO (Application Layer)
│   │   ├── __init__.py
│   │   └── use_cases.py      # Casos de uso (SpeakTextUseCase, ConfigureTTSUseCase)
│   │
│   ├── infrastructure/       # 🟡 CAMADA DE INFRAESTRUTURA (Infrastructure Layer)
│   │   ├── __init__.py
│   │   ├── tts/              # Implementações de TTS
│   │   │   ├── __init__.py
│   │   │   ├── engines.py    # GTTSEngine, Pyttsx3Engine, TTSEngineFactory
│   │   │   └── config_repository.py  # InMemoryConfigRepository
│   │   │
│   │   ├── discord/          # Implementações Discord
│   │   │   ├── __init__.py
│   │   │   └── voice_channel.py  # DiscordVoiceChannel, DiscordVoiceChannelRepository
│   │   │
│   │   ├── http/             # Servidor HTTP
│   │   │   ├── __init__.py
│   │   │   └── server.py     # HTTPServer (aiohttp)
│   │   │
│   │   └── input/            # Input listeners (keyboard, etc)
│   │       └── __init__.py
│   │
│   ├── presentation/         # 🔴 CAMADA DE APRESENTAÇÃO (Presentation Layer)
│   │   ├── __init__.py
│   │   ├── discord_commands.py  # Comandos Discord
│   │   └── http_controllers.py  # Controladores HTTP
│   │
│   └── standalone/           # 🎯 NOVA: STANDALONE CLEAN ARCHITECTURE
│       ├── __init__.py
│       │
│       ├── config/           # 🔧 STANDALONE: Configuração com Dataclasses
│       │   ├── __init__.py
│       │   └── standalone_config.py  # StandaloneConfig, ConfigurationRepository
│       │
│       ├── app/              # 🟢 STANDALONE: Aplicação Principal
│       │   ├── __init__.py
│       │   └── simple_app.py # SimpleApplication (orchestrador principal)
│       │
│       ├── services/         # 🟡 STANDALONE: Camada de Serviços
│       │   ├── __init__.py
│       │   ├── tts_services.py        # TTSProcessor
│       │   ├── hotkey_services.py     # HotkeyManager
│       │   └── notification_services.py # SystemTrayService
│       │
│       └── gui/              # 🔴 STANDALONE: Interface Gráfica
│           ├── __init__.py
│           └── simple_gui.py # ConfigurationService (Tkinter)
│
├── scripts/build/            # 🚀 BUILD SCRIPTS
│   └── build_clean_architecture.ps1  # Build único com Clean Architecture e SOLID
│
├── tts_hotkey_configurable.py      # 🎯 ENTRY POINT Principal (Clean + Fallback)
│   │
│   ├── __init__.py
│   ├── __version__.py        # Informações de versão
│   ├── bot.py                # Entry point do bot (novo)
│   ├── app.py                # Flask app (compatibilidade)
│   └── tts_hotkey.py         # 🎹 Windows hotkey listener (opcional)
│
├── tests/
│   ├── unit/                 # Testes unitários (77% coverage)
│   │   ├── core/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── presentation/
│   ├── conftest.py          # Fixtures e mocks
│   └── README.md            # Documentação de testes
│
├── .env                       # Variáveis de ambiente
├── requirements.txt           # Dependências Python
├── requirements-test.txt      # Dependências de teste
├── pytest.ini                 # Configuração de testes
├── wsgi.py                    # Entry point para Gunicorn
├── Dockerfile                 # Container Docker
└── README.md                  # Documentação
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
class SimpleApplication:
    """Orquestrador principal da aplicação."""
    def __init__(self)
    def initialize(self) -> None
    def run(self) -> None

    # Dependency injection para todos os serviços
    _config_service: ConfigurationService
    _tts_processor: TTSProcessor
    _hotkey_manager: HotkeyManager
    _notification_service: SystemTrayService
```

### 🔴 **Interface Layer** (`src/standalone/gui/`)

```python
class ConfigurationService:
    """Interface de configuração (GUI + Console)."""
    def __init__(self, prefer_gui: bool = True)
    def configure_application(self, config: StandaloneConfig) -> StandaloneConfig
    def show_gui_config(self) -> dict
    def show_console_config(self) -> dict
```

### 🚀 **Entry Point** (`tts_hotkey_configurable.py`)

```python
def main():
    """Entry point com fallback robusto."""
    try:
        # Tenta usar Clean Architecture
        from src.standalone.app.simple_app import SimpleApplication
        app = SimpleApplication()
        app.initialize()
        app.run()
    except Exception as e:
        # Fallback para implementação embutida
        print(f"Clean architecture failed: {e}")
        print("Falling back to embedded code...")
        run_embedded_standalone()
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

## 🚀 Como Executar

### Desenvolvimento Local (Python)

```bash
# Opção 1: Novo entry point (bot completo)
python -m src.bot

# Opção 2: Servidor de teste (sem Discord)
python -m src.test_server

# Opção 3: Com Flask (compatibilidade)
python -m src.app
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
docker run -d -p 10000:10000 --env-file .env tts-hotkey

# Limpar tudo
docker system prune -a
```

### Produção (Gunicorn + Docker no Render)

```bash
# Render/Docker usa wsgi.py automaticamente
gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

## ✅ Benefícios da Refatoração

### Antes (Código Antigo)

- ❌ Tudo em um único arquivo (`discord_bot.py` com 600+ linhas)
- ❌ Acoplamento alto (difícil testar)
- ❌ Lógica misturada (TTS + Discord + HTTP no mesmo lugar)
- ❌ Difícil adicionar novos engines ou plataformas
- ❌ Variáveis globais e estado compartilhado

### Depois (Código Refatorado)

- ✅ Separação clara de responsabilidades
- ✅ Fácil testar (mock de interfaces)
- ✅ Fácil adicionar novos engines TTS
- ✅ Fácil trocar Discord por outra plataforma
- ✅ Código auto-documentado e manutenível
- ✅ Dependency Injection facilita extensão

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

    use_case = SpeakTextUseCase(mock_engine, mock_repo, mock_config)
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
