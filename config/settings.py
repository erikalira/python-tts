"""Configuration management using environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv
from src.core.entities import TTSConfig


class Config:
    """Application configuration.
    
    Follows Single Responsibility: only handles configuration loading.
    """
    
    def __init__(self, env_file: Path | None = None):
        """Initialize configuration.
        
        Args:
            env_file: Path to .env file or None to use default
        """
        if env_file is None:
            env_file = Path(__file__).resolve().parents[2] / ".env"
        
        # Load environment variables
        load_dotenv(env_file, override=True)
        
        # Discord settings
        self.discord_token = os.getenv('DISCORD_TOKEN')
        self.discord_bot_port = int(os.getenv('DISCORD_BOT_PORT', '5000'))
        
        # Flask settings
        self.flask_port = int(os.getenv('PORT', os.getenv('FLASK_PORT', '8080')))
        
        # TTS settings
        self.tts_config = TTSConfig(
            engine=os.getenv('TTS_ENGINE', 'gtts').lower(),
            language=os.getenv('TTS_LANGUAGE', 'pt'),
            voice_id=os.getenv('TTS_VOICE_ID', 'roa/pt-br'),
            rate=int(os.getenv('TTS_RATE', '180'))
        )
    
    def validate(self) -> tuple[bool, str]:
        """Validate required configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.discord_token:
            return False, "DISCORD_TOKEN not set"
        
        if self.tts_config.engine not in ['gtts', 'pyttsx3']:
            return False, f"Invalid TTS_ENGINE: {self.tts_config.engine}"
        
        return True, ""
