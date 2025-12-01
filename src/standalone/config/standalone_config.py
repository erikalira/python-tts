#!/usr/bin/env python3
"""
Standalone Configuration Module - Clean Architecture
Manages configuration for the TTS Hotkey standalone application.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class TTSConfig:
    """TTS Engine configuration."""
    engine: str = "gtts"
    language: str = "pt"
    voice_id: str = "roa/pt-br"
    rate: int = 180
    output_device: Optional[str] = None


@dataclass
class DiscordConfig:
    """Discord bot configuration."""
    bot_url: str = "https://python-tts-s3z8.onrender.com"
    channel_id: Optional[str] = None
    member_id: Optional[str] = None


@dataclass
class HotkeyConfig:
    """Hotkey configuration."""
    trigger_open: str = "{"
    trigger_close: str = "}"


@dataclass
class InterfaceConfig:
    """Interface configuration."""
    show_notifications: bool = True
    console_logs: bool = True


@dataclass
class NetworkConfig:
    """Network configuration."""
    request_timeout: int = 10
    user_agent: str = "TTS-Hotkey/2.0"
    max_text_length: int = 500


@dataclass
class StandaloneConfig:
    """Main configuration container for standalone application."""
    tts: TTSConfig
    discord: DiscordConfig
    hotkey: HotkeyConfig
    interface: InterfaceConfig
    network: NetworkConfig
    
    @classmethod
    def create_default(cls) -> 'StandaloneConfig':
        """Create configuration with default values."""
        return cls(
            tts=TTSConfig(),
            discord=DiscordConfig(),
            hotkey=HotkeyConfig(),
            interface=InterfaceConfig(),
            network=NetworkConfig()
        )


class ConfigurationRepository:
    """Repository for configuration persistence."""
    
    def __init__(self, config_file_path: Optional[Path] = None):
        """Initialize with optional custom config file path."""
        self._config_file = config_file_path or Path.home() / "tts_hotkey_config.json"
    
    def load(self) -> StandaloneConfig:
        """Load configuration from file or create default."""
        if not self._config_file.exists():
            return StandaloneConfig.create_default()
        
        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return StandaloneConfig(
                tts=TTSConfig(
                    engine=data.get('tts_engine', 'gtts'),
                    language=data.get('tts_language', 'pt'),
                    voice_id=data.get('tts_voice_id', 'roa/pt-br'),
                    rate=data.get('tts_rate', 180),
                    output_device=data.get('tts_output_device')
                ),
                discord=DiscordConfig(
                    bot_url=data.get('discord_bot_url', 'https://python-tts-s3z8.onrender.com'),
                    channel_id=data.get('discord_channel_id'),
                    member_id=data.get('discord_member_id')
                ),
                hotkey=HotkeyConfig(
                    trigger_open=data.get('trigger_open', '{'),
                    trigger_close=data.get('trigger_close', '}')
                ),
                interface=InterfaceConfig(
                    show_notifications=data.get('show_notifications', True),
                    console_logs=data.get('console_logs', True)
                ),
                network=NetworkConfig(
                    request_timeout=data.get('request_timeout', 10),
                    user_agent=data.get('user_agent', 'TTS-Hotkey/2.0'),
                    max_text_length=data.get('max_text_length', 500)
                )
            )
        except Exception as e:
            print(f"[CONFIG] ⚠️ Erro ao carregar configuração: {e}")
            return StandaloneConfig.create_default()
    
    def save(self, config: StandaloneConfig) -> bool:
        """Save configuration to file."""
        try:
            data = {
                'tts_engine': config.tts.engine,
                'tts_language': config.tts.language,
                'tts_voice_id': config.tts.voice_id,
                'tts_rate': config.tts.rate,
                'tts_output_device': config.tts.output_device,
                'discord_bot_url': config.discord.bot_url,
                'discord_channel_id': config.discord.channel_id,
                'discord_member_id': config.discord.member_id,
                'trigger_open': config.hotkey.trigger_open,
                'trigger_close': config.hotkey.trigger_close,
                'show_notifications': config.interface.show_notifications,
                'console_logs': config.interface.console_logs,
                'request_timeout': config.network.request_timeout,
                'user_agent': config.network.user_agent,
                'max_text_length': config.network.max_text_length
            }
            
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"[CONFIG] ✅ Configuração salva em: {self._config_file}")
            return True
        except Exception as e:
            print(f"[CONFIG] ❌ Erro ao salvar configuração: {e}")
            return False


class EnvironmentUpdater:
    """Updates environment variables from configuration."""
    
    @staticmethod
    def update_from_config(config: StandaloneConfig) -> None:
        """Update environment variables from configuration."""
        os.environ['DISCORD_BOT_URL'] = config.discord.bot_url
        
        if config.discord.channel_id:
            os.environ['DISCORD_CHANNEL_ID'] = config.discord.channel_id
        
        if config.discord.member_id:
            os.environ['DISCORD_MEMBER_ID'] = config.discord.member_id
        
        os.environ['TTS_ENGINE'] = config.tts.engine
        os.environ['TTS_LANGUAGE'] = config.tts.language
        os.environ['TTS_VOICE_ID'] = config.tts.voice_id
        
        if config.tts.output_device:
            os.environ['TTS_OUTPUT_DEVICE'] = config.tts.output_device
        
        print(f"[CONFIG] ✅ Variáveis de ambiente atualizadas - DISCORD_MEMBER_ID: {config.discord.member_id}")


class ConfigurationValidator:
    """Validates configuration values."""
    
    @staticmethod
    def validate(config: StandaloneConfig) -> tuple[bool, list[str]]:
        """Validate configuration and return (is_valid, errors)."""
        errors = []
        
        # Discord Member ID validation (if provided)
        if config.discord.member_id and not config.discord.member_id.isdigit():
            errors.append("Discord Member ID deve conter apenas números")
        
        # TTS Rate validation
        if config.tts.rate < 50 or config.tts.rate > 500:
            errors.append("TTS Rate deve estar entre 50 e 500 WPM")
        
        # Timeout validation
        if config.network.request_timeout < 1 or config.network.request_timeout > 60:
            errors.append("Request timeout deve estar entre 1 e 60 segundos")
        
        # Max text length validation
        if config.network.max_text_length < 1 or config.network.max_text_length > 2000:
            errors.append("Comprimento máximo do texto deve estar entre 1 e 2000 caracteres")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def is_configured(config: StandaloneConfig) -> bool:
        """Check if minimum configuration is present."""
        return config.discord.member_id is not None and len(config.discord.member_id.strip()) > 0