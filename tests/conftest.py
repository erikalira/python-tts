"""Test fixtures and mocks shared across tests."""
import pytest
from unittest.mock import AsyncMock, Mock
from src.core.interfaces import ITTSEngine, IVoiceChannel, IVoiceChannelRepository, IConfigRepository, IAudioQueue
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
    
    @property
    def guild_id(self) -> int:
        """Get mock guild ID."""
        return self._guild_id


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
        self.default_config = TTSConfig(
            engine='gtts',
            language='pt',
            voice_id='roa/pt-br',
            rate=180
        )
    
    def get_config(self, guild_id: int = None) -> TTSConfig:
        """Get config by guild ID."""
        if guild_id and guild_id in self.configs:
            return self.configs[guild_id]
        return TTSConfig(
            engine=self.default_config.engine,
            language=self.default_config.language,
            voice_id=self.default_config.voice_id,
            rate=self.default_config.rate
        )
    
    def set_config(self, guild_id: int, config: TTSConfig) -> None:
        """Set config by guild ID."""
        self.configs[guild_id] = TTSConfig(
            engine=config.engine,
            language=config.language,
            voice_id=config.voice_id,
            rate=config.rate
        )
    
    async def load_from_storage(self, guild_id: int) -> TTSConfig:
        """Load config from storage mock."""
        return self.get_config(guild_id)
    
    async def save_config_async(self, guild_id: int, config: TTSConfig) -> bool:
        """Save config async mock."""
        self.set_config(guild_id, config)
        return True
    
    async def delete_config_async(self, guild_id: int) -> bool:
        """Delete config async mock."""
        self.configs.pop(guild_id, None)
        return True


class MockAudioQueue(IAudioQueue):
    """Mock audio queue for testing."""
    
    def __init__(self):
        self.items = []
        self.completed = []
    
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
        return {"size": len(self.items), "items": []}
    
    async def get_item_position(self, item_id: str) -> int:
        """Get item position."""
        for i, item in enumerate(self.items):
            if item.item_id == item_id:
                return i
        return -1
    
    async def clear_completed(self, guild_id, older_than_seconds: int = 3600):
        """Clear completed items."""
        self.completed.clear()


class MockAudioQueue(IAudioQueue):
    """Mock audio queue for testing."""
    
    def __init__(self):
        self.items = []
        self.completed = []
    
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
        return {"size": len(self.items), "items": []}
    
    async def get_item_position(self, item_id: str) -> int:
        """Get item position."""
        for i, item in enumerate(self.items):
            if item.item_id == item_id:
                return i
        return -1
    
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
