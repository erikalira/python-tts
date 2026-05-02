"""Infrastructure adapter for listing TTS voices exposed to the Discord bot."""

from __future__ import annotations

import logging

from src.application.tts_voice_catalog import TTSCatalog, TTSVoiceOption

from .pyttsx3_support import list_pyttsx3_voices

logger = logging.getLogger(__name__)

_GTTS_OPTIONS = [
    TTSVoiceOption(
        key="gtts:pt:roa-pt-br",
        engine="gtts",
        label="Google TTS - Portuguese (Brazil)",
        language="pt",
        voice_id="roa/pt-br",
    ),
    TTSVoiceOption(
        key="gtts:en:en-us", engine="gtts", label="Google TTS - English (US)", language="en", voice_id="en-us"
    ),
    TTSVoiceOption(
        key="gtts:en:en-gb", engine="gtts", label="Google TTS - English (UK)", language="en", voice_id="en-gb"
    ),
    TTSVoiceOption(key="gtts:es:roa-es", engine="gtts", label="Google TTS - Spanish", language="es", voice_id="roa/es"),
    TTSVoiceOption(key="gtts:fr:roa-fr", engine="gtts", label="Google TTS - French", language="fr", voice_id="roa/fr"),
]

_EDGE_TTS_OPTIONS = [
    TTSVoiceOption(
        key="edge-tts:pt-br-francisca",
        engine="edge-tts",
        label="Edge TTS - Francisca (PT-BR Neural)",
        language="pt-BR",
        voice_id="pt-BR-FranciscaNeural",
    ),
    TTSVoiceOption(
        key="edge-tts:pt-br-antonio",
        engine="edge-tts",
        label="Edge TTS - Antonio (PT-BR Neural)",
        language="pt-BR",
        voice_id="pt-BR-AntonioNeural",
    ),
    TTSVoiceOption(
        key="edge-tts:en-us-aria",
        engine="edge-tts",
        label="Edge TTS - Aria (EN-US Neural)",
        language="en-US",
        voice_id="en-US-AriaNeural",
    ),
    TTSVoiceOption(
        key="edge-tts:en-us-jenny",
        engine="edge-tts",
        label="Edge TTS - Jenny (EN-US Neural)",
        language="en-US",
        voice_id="en-US-JennyNeural",
    ),
    TTSVoiceOption(
        key="edge-tts:en-us-guy",
        engine="edge-tts",
        label="Edge TTS - Guy (EN-US Neural)",
        language="en-US",
        voice_id="en-US-GuyNeural",
    ),
    TTSVoiceOption(
        key="edge-tts:en-gb-sonia",
        engine="edge-tts",
        label="Edge TTS - Sonia (EN-GB Neural)",
        language="en-GB",
        voice_id="en-GB-SoniaNeural",
    ),
    TTSVoiceOption(
        key="edge-tts:es-es-elvira",
        engine="edge-tts",
        label="Edge TTS - Elvira (ES-ES Neural)",
        language="es-ES",
        voice_id="es-ES-ElviraNeural",
    ),
    TTSVoiceOption(
        key="edge-tts:fr-fr-denise",
        engine="edge-tts",
        label="Edge TTS - Denise (FR-FR Neural)",
        language="fr-FR",
        voice_id="fr-FR-DeniseNeural",
    ),
]


class RuntimeTTSCatalog(TTSCatalog):
    """Expose runtime-selectable voices for Discord command autocomplete."""

    def __init__(self) -> None:
        self._cached_pyttsx3_options: list[TTSVoiceOption] | None = None

    def list_voice_options(self) -> list[TTSVoiceOption]:
        return [*_GTTS_OPTIONS, *_EDGE_TTS_OPTIONS, *self._get_pyttsx3_options()]

    def get_voice_option(self, key: str) -> TTSVoiceOption | None:
        normalized_key = key.strip().lower()
        for option in self.list_voice_options():
            if option.key.lower() == normalized_key:
                return option
        return None

    def find_voice_option(self, *, engine: str, language: str, voice_id: str) -> TTSVoiceOption | None:
        normalized_engine = engine.lower()
        normalized_language = language.lower()
        normalized_voice_id = voice_id.lower()
        for option in self.list_voice_options():
            if (
                option.engine == normalized_engine
                and option.language.lower() == normalized_language
                and option.voice_id.lower() == normalized_voice_id
            ):
                return option
        return None

    def is_voice_available(self, *, engine: str, voice_id: str) -> bool:
        normalized_engine = engine.lower()
        if not voice_id.strip():
            return False
        return any(
            option.engine == normalized_engine and option.voice_id.lower() == voice_id.lower()
            for option in self.list_voice_options()
        )

    def _get_pyttsx3_options(self) -> list[TTSVoiceOption]:
        if self._cached_pyttsx3_options is None:
            self._cached_pyttsx3_options = self._list_pyttsx3_options()
        return list(self._cached_pyttsx3_options)

    def _list_pyttsx3_options(self) -> list[TTSVoiceOption]:
        options: list[TTSVoiceOption] = []
        seen_values: set[str] = set()

        for voice in list_pyttsx3_voices(logger):
            voice_name = (getattr(voice, "name", "") or "").strip()
            voice_id = (getattr(voice, "id", "") or "").strip()
            if not voice_id:
                continue

            candidate_value = voice_name or voice_id.split("\\")[-1] or voice_id
            if len(candidate_value) > 100:
                candidate_value = voice_id.split("\\")[-1][:100]

            value_key = candidate_value.lower()
            if not candidate_value or value_key in seen_values:
                continue

            seen_values.add(value_key)
            label = f"R.E.P.O. - {voice_name or candidate_value}"
            if len(label) > 100:
                label = label[:97] + "..."

            options.append(
                TTSVoiceOption(
                    key=f"pyttsx3:{value_key}",
                    engine="pyttsx3",
                    label=label,
                    language="system",
                    voice_id=candidate_value,
                )
            )

        return options
