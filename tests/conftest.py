"""Test fixtures and mocks shared across tests."""
import pytest
from unittest.mock import AsyncMock, Mock
from src.core.interfaces import ITTSEngine, IVoiceChannel, IVoiceChannelRepository, IConfigRepository
from src.core.entities import TTSConfig, AudioFile, TTSRequest


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
    
    def __init__(self):
        self.connected = False
        self.played_audio = []
    
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
        return 123456


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
    
    def get_config(self, user_id: int = None) -> TTSConfig:
        """Get config."""
        if user_id and user_id in self.configs:
            return self.configs[user_id]
        return self.default_config
    
    def set_config(self, user_id: int, config: TTSConfig) -> None:
        """Set config."""
        self.configs[user_id] = config


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
