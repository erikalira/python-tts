"""Compatibility facade for shared application use cases."""

from src.application.speak_use_case import SpeakTextUseCase
from src.application.tts_config_use_case import ConfigureTTSUseCase
from src.application.voice_channel_use_cases import (
    GetCurrentVoiceContextUseCase,
    JoinVoiceChannelUseCase,
    LeaveVoiceChannelUseCase,
)

__all__ = [
    "JoinVoiceChannelUseCase",
    "LeaveVoiceChannelUseCase",
    "GetCurrentVoiceContextUseCase",
    "SpeakTextUseCase",
    "ConfigureTTSUseCase",
]
