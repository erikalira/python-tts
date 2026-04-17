# 🤝 Contributing to TTS Hotkey Windows

Obrigado pelo interesse em contribuir! Este projeto segue **Clean Architecture** e os princípios **SOLID**.

## 📐 Arquitetura do Projeto

Este projeto é estruturado em camadas seguindo **Clean Architecture**:

```
src/
├── core/                 # 🔵 DOMÍNIO (Domain Layer)
│   ├── entities.py       # Entidades puras de negócio
│   └── interfaces.py     # Contratos/Interfaces (abstrações)
│
├── application/          # 🟢 APLICAÇÃO (Application Layer)
│   └── use_cases.py      # Regras de negócio e orquestração
│
├── infrastructure/       # 🟡 INFRAESTRUTURA (Infrastructure Layer)
│   ├── tts/              # Implementações de TTS
│   ├── discord/          # Implementações Discord
│   └── http/             # Servidor HTTP
│
└── presentation/         # 🔴 APRESENTAÇÃO (Presentation Layer)
    ├── http_controllers.py   # Controllers HTTP
    └── discord_commands.py   # Comandos Discord
```

### 🎯 Regras de Dependência

**IMPORTANTE**: As dependências devem sempre apontar para **dentro** (camadas externas dependem das internas):

```
Presentation → Application → Domain ← Infrastructure
     ↓              ↓           ↑
  Controllers   Use Cases   Entities/Interfaces
```

- ✅ **Presentation** pode depender de **Application** e **Domain**
- ✅ **Application** pode depender de **Domain**
- ✅ **Infrastructure** implementa interfaces do **Domain**
- ❌ **Domain** NÃO pode depender de nada (puro Python)
- ❌ **Application** NÃO pode depender de **Infrastructure** diretamente

## 🎓 Princípios SOLID Obrigatórios

### 1. **S**ingle Responsibility Principle (SRP)

✅ **FAÇA**: Cada classe deve ter uma única responsabilidade

```python
# ✅ BOM - Uma responsabilidade: gerar áudio com gTTS
class GTTSEngine(ITTSEngine):
    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        # Apenas gera áudio
        pass
```

❌ **NÃO FAÇA**: Misturar responsabilidades

```python
# ❌ RUIM - Muitas responsabilidades
class TTSService:
    def generate_audio(self, text): pass  # TTS
    def send_to_discord(self, audio): pass  # Discord
    def log_request(self, request): pass  # Logging
```

### 2. **O**pen/Closed Principle (OCP)

✅ **FAÇA**: Aberto para extensão, fechado para modificação

```python
# ✅ BOM - Adicione novos engines sem modificar código existente
class ElevenLabsEngine(ITTSEngine):  # Nova implementação
    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        # Nova lógica aqui
        pass
```

❌ **NÃO FAÇA**: Modificar código existente para adicionar funcionalidades

```python
# ❌ RUIM - Modificando classe existente
class GTTSEngine:
    async def generate_audio(self, text: str, use_elevenlabs: bool = False):
        if use_elevenlabs:  # ❌ Não adicione condicionais para novos engines
            # ...
```

### 3. **L**iskov Substitution Principle (LSP)

✅ **FAÇA**: Implementações devem ser substituíveis por suas interfaces

```python
# ✅ BOM - Qualquer ITTSEngine funciona no use case
class SpeakTextUseCase:
    def __init__(self, tts_engine: ITTSEngine):  # Aceita qualquer implementação
        self._tts_engine = tts_engine
```

### 4. **I**nterface Segregation Principle (ISP)

✅ **FAÇA**: Interfaces pequenas e específicas

```python
# ✅ BOM - Interface focada
class ITTSEngine(ABC):
    @abstractmethod
    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        pass
```

❌ **NÃO FAÇA**: Interfaces gordas com métodos não relacionados

```python
# ❌ RUIM - Interface muito grande
class ITTSService(ABC):
    async def generate_audio(self): pass
    async def connect_to_discord(self): pass  # ❌ Não relacionado
    async def save_to_database(self): pass  # ❌ Não relacionado
```

### 5. **D**ependency Inversion Principle (DIP)

✅ **FAÇA**: Dependa de abstrações (interfaces), não de implementações

```python
# ✅ BOM - Use case depende de interface
class SpeakTextUseCase:
    def __init__(
        self,
        tts_engine: ITTSEngine,  # ✅ Interface
        channel_repository: IVoiceChannelRepository  # ✅ Interface
    ):
        self._tts_engine = tts_engine
        self._channel_repository = channel_repository
```

❌ **NÃO FAÇA**: Depender de implementações concretas

```python
# ❌ RUIM - Use case depende de implementação concreta
class SpeakTextUseCase:
    def __init__(self):
        self._tts_engine = GTTSEngine()  # ❌ Implementação concreta
        self._repository = DiscordVoiceChannelRepository()  # ❌ Implementação concreta
```

## 📝 Checklist para Pull Requests

Antes de submeter seu PR, verifique:

### ✅ Arquitetura

- [ ] Código está na camada correta
- [ ] Dependências apontam para dentro (não viola Clean Architecture)
- [ ] Não há import circular
- [ ] Interfaces estão em `core/interfaces.py`
- [ ] Entidades estão em `core/entities.py`

### ✅ SOLID

- [ ] **SRP**: Cada classe tem uma única responsabilidade
- [ ] **OCP**: Novo código não modifica classes existentes
- [ ] **LSP**: Implementações seguem contratos das interfaces
- [ ] **ISP**: Não cria interfaces "gordas"
- [ ] **DIP**: Use cases dependem de interfaces, não de implementações concretas

### ✅ Testes

- [ ] Testes unitários para novas classes
- [ ] Coverage mantém ou melhora (mínimo 77%)
- [ ] Mocks usam interfaces, não implementações concretas
- [ ] Testes rodam com `pytest`

### ✅ Código Limpo

- [ ] Nomes descritivos (classes, métodos, variáveis)
- [ ] Métodos pequenos (máximo ~20 linhas)
- [ ] Sem código comentado
- [ ] Docstrings em classes e métodos públicos
- [ ] Type hints em todos os métodos

### ✅ Documentação

- [ ] README.md atualizado (se necessário)
- [ ] docs/architecture/ARCHITECTURE.md atualizado (se mudou arquitetura)
- [ ] Comentários explicam "por quê", não "o quê"

## 🔨 Como Adicionar Novas Funcionalidades

### Exemplo: Adicionar novo TTS Engine

1. **Crie a interface no Domain** (se não existir):

```python
# src/core/interfaces.py
class ITTSEngine(ABC):
    @abstractmethod
    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        pass
```

2. **Implemente na Infrastructure**:

```python
# src/infrastructure/tts/engines.py
class ElevenLabsEngine(ITTSEngine):
    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        # Implementação aqui
        pass
```

3. **Registre no Factory**:

```python
# src/infrastructure/tts/engines.py
class TTSEngineFactory:
    def create(self, engine_type: str) -> ITTSEngine:
        if engine_type == 'elevenlabs':
            return ElevenLabsEngine()
        # ...
```

4. **Adicione testes**:

```python
# tests/unit/infrastructure/tts/test_engines.py
@pytest.mark.asyncio
async def test_elevenlabs_engine_generates_audio():
    engine = ElevenLabsEngine()
    audio = await engine.generate_audio("test", TTSConfig())
    assert audio.path.endswith('.wav')
```

## 🚨 O Que NÃO Fazer

### ❌ Não misture camadas:

```python
# ❌ RUIM - Use case importando implementation
from src.infrastructure.tts.engines import GTTSEngine

class SpeakTextUseCase:
    def __init__(self):
        self._engine = GTTSEngine()  # ❌ Violação do DIP
```

### ❌ Não coloque lógica de negócio na Presentation:

```python
# ❌ RUIM - Controller com lógica de negócio
class SpeakController:
    async def speak(self, request):
        # ❌ Lógica de negócio aqui
        if not voice_channel:
            config = get_config()
            audio = generate_audio()
        # ...
```

### ❌ Não acople Domain à Infrastructure:

```python
# ❌ RUIM - Entidade com dependência externa
# src/core/entities.py
import discord  # ❌ Nunca!

@dataclass
class TTSRequest:
    text: str
    discord_client: discord.Client  # ❌ Acoplamento!
```

## 📚 Recursos

- **Clean Architecture**: [Uncle Bob - Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- **SOLID Principles**: [SOLID Principles Explained](https://www.digitalocean.com/community/conceptual_articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
- **Dependency Injection**: [Python DI Guide](https://python-dependency-injector.ets-labs.org/)

## 🐛 Reportando Bugs

1. Verifique se o bug já foi reportado
2. Inclua steps para reproduzir
3. Inclua logs relevantes
4. Mencione versão do Python e OS

## ❓ Dúvidas

Abra uma **Issue** com a tag `question` ou entre em contato!

---

**Lembre-se**: Código limpo e bem estruturado é tão importante quanto funcionalidade. Obrigado por contribuir! 🚀
