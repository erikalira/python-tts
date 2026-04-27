"""Test fixtures and mocks shared across tests."""
import pytest
from src.application.dto import AudioQueueStatusDTO
from src.application.tts_queue_orchestrator import TTSQueueOrchestrator
from src.application.tts_voice_catalog import TTSVoiceOption
from src.application.use_cases import SpeakTextUseCase
from src.application.voice_channel_resolution import VoiceChannelResolutionService
from src.core.interfaces import ITTSEngine, IVoiceChannel, IVoiceChannelRepository, IConfigRepository, IAudioQueue, IAudioFileCleanup
from src.core.entities import TTSConfig, AudioFile, TTSRequest, AudioQueueItem


class MockTTSEngine(ITTSEngine):
    """Mock TTS engine for testing."""
    
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.calls = []
    
    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        """Generate mock audio."""
        self.calls.append({'text': text, 'config': config})
        if self.should_fail:
            raise Exception("Mock TTS error")
        return AudioFile(path="/tmp/mock_audio.wav")


class MockVoiceChannel(IVoiceChannel):
    """Mock voice channel for testing."""
    
    def __init__(self, channel_id: int = 123456, guild_id: int = 789012):
        self.connected = False
        self.played_audio = []
        self._channel_id = channel_id
        self._guild_id = guild_id
    
    async def connect(self) -> None:
        """Mock connect."""
        self.connected = True
    
    async def disconnect(self) -> None:
        """Mock disconnect."""
        self.connected = False
    
    async def play_audio(self, audio: AudioFile) -> None:
        """Mock play audio."""
        if not self.connected:
            raise RuntimeError("Not connected to voice channel")
        self.played_audio.append(audio.path)
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.connected

    def get_channel_id(self) -> int:
        """Get mock channel ID."""
        return self._channel_id

    def get_channel_name(self) -> str:
        """Get mock channel name."""
        return "Mock Voice"

    def get_guild_id(self) -> int:
        """Get mock guild ID."""
        return self._guild_id

    def get_guild_name(self) -> str:
        """Get mock guild name."""
        return "Mock Guild"


class MockVoiceChannelRepository(IVoiceChannelRepository):
    """Mock voice channel repository for testing."""
    
    def __init__(self, channel=None, return_none=False):
        self.channel = channel or MockVoiceChannel()
        self.return_none = return_none
    
    async def find_connected_channel(self):
        """Mock find connected channel."""
        return None if self.return_none else self.channel
    
    async def find_by_member_id(self, member_id: int):
        """Mock find by member ID."""
        return None if self.return_none else self.channel
    
    async def find_by_channel_id(self, channel_id: int):
        """Mock find by channel ID."""
        return None if self.return_none else self.channel
    
    async def find_by_guild_id(self, guild_id: int):
        """Mock find by guild ID."""
        return None if self.return_none else self.channel


class MockConfigRepository(IConfigRepository):
    """Mock config repository for testing."""
    
    def __init__(self):
        self.configs = {}
        self.user_configs = {}
        self.default_config = TTSConfig(
            engine='gtts',
            language='pt',
            voice_id='roa/pt-br',
            rate=180
        )
    
    def get_config(self, guild_id: int = None, user_id: int | None = None) -> TTSConfig:
        """Get config by guild ID."""
        if guild_id and user_id and (guild_id, user_id) in self.user_configs:
            return self.user_configs[(guild_id, user_id)]
        if guild_id and guild_id in self.configs:
            return self.configs[guild_id]
        return TTSConfig(
            engine=self.default_config.engine,
            language=self.default_config.language,
            voice_id=self.default_config.voice_id,
            rate=self.default_config.rate
        )

    async def load_config_async(self, guild_id: int = None, user_id: int | None = None) -> TTSConfig:
        """Load config through the async repository contract."""
        return self.get_config(guild_id, user_id=user_id)
    
    def set_config(self, guild_id: int, config: TTSConfig, user_id: int | None = None) -> None:
        """Set config by guild ID."""
        target = TTSConfig(
            engine=config.engine,
            language=config.language,
            voice_id=config.voice_id,
            rate=config.rate
        )
        if user_id is not None:
            self.user_configs[(guild_id, user_id)] = target
            return
        self.configs[guild_id] = target
    
    async def load_from_storage(self, guild_id: int, user_id: int | None = None) -> TTSConfig:
        """Load config from storage mock."""
        return self.get_config(guild_id, user_id=user_id)
    
    async def save_config_async(self, guild_id: int, config: TTSConfig, user_id: int | None = None) -> bool:
        """Save config async mock."""
        self.set_config(guild_id, config, user_id=user_id)
        return True
    
    async def delete_config_async(self, guild_id: int, user_id: int | None = None) -> bool:
        """Delete config async mock."""
        if user_id is not None:
            self.user_configs.pop((guild_id, user_id), None)
            return True
        self.configs.pop(guild_id, None)
        return True

    def get_effective_scope(self, guild_id: int = None, user_id: int | None = None) -> str:
        if guild_id and user_id and (guild_id, user_id) in self.user_configs:
            return "user"
        if guild_id and guild_id in self.configs:
            return "guild"
        return "default"


class MockAudioCleanup(IAudioFileCleanup):
    """Mock audio cleanup adapter for testing."""

    def __init__(self):
        self.cleaned_paths = []

    async def cleanup(self, audio: AudioFile) -> None:
        self.cleaned_paths.append(audio.path)


class MockTTSCatalog:
    """Mock catalog for presentation tests that expose voice options."""

    def __init__(self):
        self.options = {
            "gtts:pt:roa-pt-br": TTSVoiceOption(
                key="gtts:pt:roa-pt-br",
                engine="gtts",
                label="Google TTS - Portuguese (Brazil)",
                language="pt",
                voice_id="roa/pt-br",
            ),
            "pyttsx3:david": TTSVoiceOption(
                key="pyttsx3:david",
                engine="pyttsx3",
                label="R.E.P.O. - Microsoft David",
                language="system",
                voice_id="David",
            ),
            "pyttsx3:maria": TTSVoiceOption(
                key="pyttsx3:maria",
                engine="pyttsx3",
                label="R.E.P.O. - Microsoft Maria",
                language="system",
                voice_id="Maria",
            ),
            "edge-tts:pt-br-francisca": TTSVoiceOption(
                key="edge-tts:pt-br-francisca",
                engine="edge-tts",
                label="Edge TTS - Francisca (PT-BR Neural)",
                language="pt-BR",
                voice_id="pt-BR-FranciscaNeural",
            ),
        }

    def list_voice_options(self) -> list[TTSVoiceOption]:
        return list(self.options.values())

    def get_voice_option(self, key: str) -> TTSVoiceOption | None:
        return self.options.get(key)

    def find_voice_option(self, *, engine: str, language: str, voice_id: str) -> TTSVoiceOption | None:
        for option in self.options.values():
            if option.engine == engine and option.language == language and option.voice_id == voice_id:
                return option
        return None

    def is_voice_available(self, *, engine: str, voice_id: str) -> bool:
        return any(
            option.engine == engine and option.voice_id.lower() == voice_id.lower()
            for option in self.options.values()
        )

class MockAudioQueue(IAudioQueue):
    """Mock audio queue for testing."""
    
    def __init__(self):
        self.items = []
        self.completed = []
        self.processing_guilds = set()
    
    async def enqueue(self, item: AudioQueueItem) -> str | None:
        """Add item to queue."""
        self.items.append(item)
        return item.item_id
    
    async def dequeue(self, guild_id):
        """Remove and return next item."""
        if self.items:
            return self.items.pop(0)
        return None
    
    async def peek_next(self, guild_id):
        """Look at next item."""
        return self.items[0] if self.items else None
    
    async def get_queue_status(self, guild_id):
        """Get queue status."""
        return AudioQueueStatusDTO(size=len(self.items), items=[])
    
    async def get_item_position(self, item_id: str) -> int:
        """Get item position."""
        for i, item in enumerate(self.items):
            if item.item_id == item_id:
                return i
        return -1

    async def update_item(self, item: AudioQueueItem) -> None:
        """Persist in-memory item updates for tests."""
        for index, existing_item in enumerate(self.items):
            if existing_item.item_id == item.item_id:
                self.items[index] = item
                return

    async def renew_guild_lock(self, guild_id, owner_token: str, ttl_seconds: int = 30) -> bool:
        """Renew a mock guild lock."""
        del ttl_seconds
        return True

    async def acquire_processing_lease(self, guild_id, owner_token: str, ttl_seconds: int = 30) -> bool:
        del owner_token, ttl_seconds
        if guild_id in self.processing_guilds:
            return False
        self.processing_guilds.add(guild_id)
        return True

    async def release_processing_lease(self, guild_id, owner_token: str) -> None:
        del owner_token
        self.processing_guilds.discard(guild_id)

    async def renew_processing_lease(self, guild_id, owner_token: str, ttl_seconds: int = 30) -> bool:
        del owner_token, ttl_seconds
        return guild_id in self.processing_guilds

    async def is_guild_processing(self, guild_id) -> bool:
        return guild_id in self.processing_guilds
    
    async def clear_completed(self, guild_id, older_than_seconds: int = 3600):
        """Clear completed items."""
        self.completed.clear()


# Pytest fixtures
@pytest.fixture
def mock_tts_engine():
    """Fixture for mock TTS engine."""
    return MockTTSEngine()


@pytest.fixture
def mock_voice_channel():
    """Fixture for mock voice channel."""
    return MockVoiceChannel()


@pytest.fixture
def mock_channel_repository(mock_voice_channel):
    """Fixture for mock channel repository."""
    return MockVoiceChannelRepository(mock_voice_channel)


@pytest.fixture
def mock_config_repository():
    """Fixture for mock config repository."""
    return MockConfigRepository()


@pytest.fixture
def mock_audio_queue():
    """Fixture for mock audio queue."""
    return MockAudioQueue()


@pytest.fixture
def mock_audio_cleanup():
    """Fixture for mock audio cleanup."""
    return MockAudioCleanup()


@pytest.fixture
def mock_tts_catalog():
    """Fixture for mock TTS catalog."""
    return MockTTSCatalog()


@pytest.fixture
def build_speak_use_case(mock_audio_cleanup):
    """Factory for SpeakTextUseCase with explicit collaborators."""

    def _build(
        *,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        max_text_length=None,
        queue_runtime_is_active=None,
    ):
        voice_channel_resolution = VoiceChannelResolutionService(mock_channel_repository)
        queue_orchestrator = TTSQueueOrchestrator(
            tts_engine=mock_tts_engine,
            config_repository=mock_config_repository,
            audio_queue=mock_audio_queue,
            voice_channel_resolution=voice_channel_resolution,
            audio_cleanup=mock_audio_cleanup,
        )
        return SpeakTextUseCase(
            channel_repository=mock_channel_repository,
            audio_queue=mock_audio_queue,
            voice_channel_resolution=voice_channel_resolution,
            queue_orchestrator=queue_orchestrator,
            max_text_length=max_text_length,
            queue_runtime_is_active=queue_runtime_is_active or (lambda: True),
        )

    return _build


@pytest.fixture
def sample_tts_request():
    """Fixture for sample TTS request."""
    return TTSRequest(
        text="Hello world",
        channel_id=123456,
        guild_id=789012,
        member_id=345678
    )


@pytest.fixture
def sample_tts_config():
    """Fixture for sample TTS config."""
    return TTSConfig(
        engine='gtts',
        language='en',
        voice_id='en-us',
        rate=180
    )
