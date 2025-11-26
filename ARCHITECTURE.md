# Arquitetura do Projeto - TTS Hotkey Windows

## 📐 Visão Geral

Este projeto foi refatorado seguindo **Clean Architecture** e os princípios **SOLID** para garantir:
- ✅ Código modular e testável
- ✅ Baixo acoplamento entre camadas
- ✅ Alta coesão dentro dos módulos
- ✅ Facilidade de manutenção e extensão
- ✅ Independência de frameworks externos

## 🏗️ Estrutura de Diretórios

```
tts-hotkey-windows/
├── config/                    # Configuração e Dependency Injection
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
│   │   ├── http_controllers.py   # SpeakController (endpoints HTTP)
│   │   └── discord_commands.py   # DiscordCommands (slash commands)
│   │
│   ├── __init__.py
│   ├── __version__.py        # Informações de versão
│   ├── bot.py                # Entry point do bot (novo)
│   ├── app.py                # Flask app (compatibilidade)
│   ├── discord_bot.py        # ⚠️ LEGADO (manter por compatibilidade)
│   ├── tts_hotkey.py         # ⚠️ LEGADO (manter por compatibilidade)
│   └── run_with_flask.py     # ⚠️ LEGADO (manter por compatibilidade)
│
├── .env                       # Variáveis de ambiente
├── requirements.txt           # Dependências Python
├── wsgi.py                    # Entry point para Gunicorn
├── Dockerfile                 # Container Docker
└── README.md                  # Documentação
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

### Desenvolvimento Local
```bash
# Opção 1: Novo entry point
python -m src.bot

# Opção 2: Com Flask (compatibilidade)
python -m src.app
```

### Produção (Gunicorn + Docker)
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

## 📝 Migração dos Arquivos Legados

Os arquivos antigos foram mantidos para compatibilidade:
- `discord_bot.py` - pode ser removido após validação
- `tts_hotkey.py` - mantido para funcionalidade de hotkey (precisa ser refatorado)
- `run_with_flask.py` - substituído por `app.py`

**Próximos passos:**
1. Refatorar `tts_hotkey.py` usando a nova arquitetura
2. Criar testes unitários para cada camada
3. Documentar APIs e contratos
4. Adicionar logging estruturado

## 🎓 Referências

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Dependency Injection in Python](https://python-dependency-injector.ets-labs.org/)
