"""Infrastructure layer - TTS engines implementation."""

import asyncio
import json
import logging
import os
import tempfile
from dataclasses import dataclass, field
from typing import cast

import aiohttp
import pyttsx3
from gtts import gTTS

from src.core.entities import DEFAULT_FISH_AUDIO_MODEL, AudioFile, TTSConfig
from src.core.interfaces import ITTSEngine
from src.infrastructure.tts.pyttsx3_support import Pyttsx3EngineLike, configure_pyttsx3_engine

logger = logging.getLogger(__name__)

FISH_AUDIO_TTS_URL = "https://api.fish.audio/v1/tts"

_FISH_AUDIO_DOWNLOAD_CHUNK_BYTES = 64 * 1024
_FISH_AUDIO_ERROR_DETAIL_LIMIT = 300


def _create_temp_audio_path(suffix: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        return tmp.name


def _remove_temp_audio_file(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        return
    except OSError as exc:
        logger.warning("Failed to remove temporary audio file %s: %s", path, exc)


def _cleanup_temp_audio_file_when_done(future: asyncio.Future, path: str) -> None:
    def _cleanup(_future) -> None:
        _remove_temp_audio_file(path)

    future.add_done_callback(_cleanup)


class GTTSEngine(ITTSEngine):
    """Google Text-to-Speech engine implementation.

    Follows Single Responsibility: only handles gTTS audio generation.
    """

    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        """Generate audio using Google TTS.

        Args:
            text: Text to convert
            config: TTS configuration

        Returns:
            AudioFile with generated audio path
        """
        loop = asyncio.get_running_loop()
        tmpname = _create_temp_audio_path(".mp3")
        generation_future = loop.run_in_executor(None, self._generate_sync, text, config, tmpname)

        try:
            await asyncio.shield(generation_future)
            return AudioFile(path=tmpname)
        except asyncio.CancelledError:
            logger.warning("gTTS audio generation cancelled; scheduling cleanup for %s", tmpname)
            _cleanup_temp_audio_file_when_done(generation_future, tmpname)
            raise
        except Exception:
            _remove_temp_audio_file(tmpname)
            raise

    def _generate_sync(self, text: str, config: TTSConfig, output_path: str):
        """Synchronous audio generation."""
        tts = gTTS(text=text, lang=config.language)
        tts.save(output_path)


class Pyttsx3Engine(ITTSEngine):
    """Pyttsx3 TTS engine implementation (espeak-ng on Linux, SAPI5 on Windows).

    Follows Single Responsibility: only handles pyttsx3 audio generation.
    """

    def __init__(self):
        """Initialize pyttsx3 engine."""
        self._engine: pyttsx3.Engine | None = None
        self._initialized = False

    def _initialize_engine(self, config: TTSConfig):
        """Lazy initialization of pyttsx3 engine."""
        if self._initialized:
            return

        try:
            import platform

            if platform.system() == "Windows":
                logger.info("🎤 Initializing TTS with SAPI5 (Windows native)")
                self._engine = pyttsx3.init(driverName="sapi5")
            else:
                logger.info("🎤 Initializing TTS with pyttsx3 (espeak-ng on Linux)")
                self._engine = pyttsx3.init()

            if self._engine:
                configure_pyttsx3_engine(cast(Pyttsx3EngineLike, self._engine), config, logger)
                self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            raise

    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        """Generate audio using pyttsx3.

        Args:
            text: Text to convert
            config: TTS configuration

        Returns:
            AudioFile with generated audio path
        """
        self._initialize_engine(config)
        if self._engine:
            configure_pyttsx3_engine(cast(Pyttsx3EngineLike, self._engine), config, logger)

        loop = asyncio.get_running_loop()
        tmpname = _create_temp_audio_path(".wav")
        generation_future = loop.run_in_executor(None, self._generate_sync, text, tmpname)

        try:
            await asyncio.shield(generation_future)
            return AudioFile(path=tmpname)
        except asyncio.CancelledError:
            logger.warning("pyttsx3 audio generation cancelled; scheduling cleanup for %s", tmpname)
            _cleanup_temp_audio_file_when_done(generation_future, tmpname)
            raise
        except Exception:
            _remove_temp_audio_file(tmpname)
            raise

    def _generate_sync(self, text: str, output_path: str):
        """Synchronous audio generation."""
        if not self._engine:
            raise RuntimeError("TTS engine not initialized")

        self._engine.save_to_file(text, output_path)
        self._engine.runAndWait()


class EdgeTTSEngine(ITTSEngine):
    """Microsoft Edge online TTS engine implementation."""

    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        try:
            import edge_tts
        except ImportError as exc:
            raise RuntimeError("edge-tts is not installed") from exc

        tmpname = _create_temp_audio_path(".mp3")

        communicate = edge_tts.Communicate(
            text=text,
            voice=config.voice_id,
            rate=self._map_rate(config.rate),
        )
        try:
            await communicate.save(tmpname)
            return AudioFile(path=tmpname)
        except asyncio.CancelledError:
            logger.warning("edge-tts audio generation cancelled; cleaning up %s", tmpname)
            _remove_temp_audio_file(tmpname)
            raise
        except Exception:
            _remove_temp_audio_file(tmpname)
            raise

    @staticmethod
    def _map_rate(rate: int) -> str:
        baseline = 180
        delta = round(((rate - baseline) / baseline) * 100)
        clamped = max(-50, min(100, delta))
        sign = "+" if clamped >= 0 else ""
        return f"{sign}{clamped}%"


@dataclass(frozen=True)
class FishAudioSettings:
    """Credential and model selection for the Fish Audio provider.

    Frozen so the credential cannot be mutated after the container wires it.
    ``api_key`` is excluded from ``repr`` because frozen protects integrity, not
    confidentiality: an auto-generated repr would disclose the credential in any
    debug log, assertion diff, or structure dump that happens to contain it.
    """

    api_key: str = field(default="", repr=False)
    model: str = DEFAULT_FISH_AUDIO_MODEL

    @property
    def is_configured(self) -> bool:
        """Return whether a usable API key is present."""
        return bool(self.api_key.strip())


class FishAudioError(RuntimeError):
    """Fish Audio synthesis failure carrying an operator-readable message.

    Messages built by this engine never embed the API key.
    """


class FishAudioEngine(ITTSEngine):
    """Fish Audio HTTP TTS engine (s2.1-pro family).

    The voice is supplied by the user as a ``reference_id`` carried in
    ``TTSConfig.voice_id``; this engine owns no voice catalog and does not check
    that a voice exists before synthesizing.
    """

    def __init__(self, settings: FishAudioSettings):
        """Initialize with the provider credential and model identifier."""
        self._settings = settings

    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        """Generate audio using the Fish Audio API.

        Args:
            text: Text to convert
            config: TTS configuration whose ``voice_id`` is a Fish reference_id

        Returns:
            AudioFile with generated audio path

        Raises:
            FishAudioError: If the credential is missing or the API refuses
        """
        if not self._settings.is_configured:
            raise FishAudioError("Fish Audio API key is not configured; set FISH_AUDIO")

        tmpname = _create_temp_audio_path(".mp3")
        try:
            await self._synthesize_to_file(text, config, tmpname)
            return AudioFile(path=tmpname)
        except asyncio.CancelledError:
            logger.warning("Fish Audio generation cancelled; cleaning up %s", tmpname)
            _remove_temp_audio_file(tmpname)
            raise
        except Exception:
            _remove_temp_audio_file(tmpname)
            raise

    async def _synthesize_to_file(self, text: str, config: TTSConfig, output_path: str) -> None:
        """Stream one synthesis response into ``output_path``.

        No client-side timeout is set here: the attempt is bounded by the
        orchestrator's TTS generation timeout, which cancels this coroutine and
        lets ``generate_audio`` clean up. A second timeout would duplicate that
        budget with a number this layer does not know.
        """
        payload: dict[str, object] = {
            "text": text,
            "reference_id": config.voice_id,
            "format": "mp3",
            # The Fish voice model determines the spoken language, so
            # config.language is deliberately not sent.
            "prosody": {"speed": self._map_rate(config.rate)},
        }
        headers = {
            "Authorization": f"Bearer {self._settings.api_key}",
            "Content-Type": "application/json",
            "model": self._settings.model,
        }

        written = 0
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    FISH_AUDIO_TTS_URL, json=payload, headers=headers, allow_redirects=False
                ) as response,
            ):
                if response.status != 200:
                    body = await response.text()
                    raise FishAudioError(self._describe_failure(response.status, body, config.voice_id))

                with open(output_path, "wb") as audio_file:
                    async for chunk in response.content.iter_chunked(_FISH_AUDIO_DOWNLOAD_CHUNK_BYTES):
                        audio_file.write(chunk)
                        written += len(chunk)
        except TimeoutError as exc:
            # Checked before ClientError: aiohttp.ServerTimeoutError subclasses
            # both, and "timed out" is the more useful message for it.
            raise FishAudioError("Fish Audio request timed out") from exc
        except aiohttp.ClientError as exc:
            # Surface transport failures as this engine's error type so callers
            # report a Fish Audio problem instead of a raw aiohttp error.
            #
            # str(exc), never repr(exc): aiohttp.ClientResponseError's repr
            # includes request_info.headers, which carries Authorization. This
            # message reaches the Redis queue item and an OTel span, so a
            # "cleanup" to {exc!r} here would be a live credential leak.
            # Redacted as well, so the invariant is enforced and not merely true.
            detail = self._redact_api_key(f"{type(exc).__name__}: {exc}")
            raise FishAudioError(f"Fish Audio request failed: {detail}") from exc

        if written == 0:
            # A 200 with an empty stream would otherwise be played as silence.
            raise FishAudioError("Fish Audio returned an empty audio stream")

    def _describe_failure(self, status: int, body: str, voice_id: str) -> str:
        """Build an actionable message for a non-200 response."""
        detail = self._extract_detail(body)
        if status == 401:
            return "Fish Audio rejected the API key (401). Verify the FISH_AUDIO value."
        if status == 402:
            return (
                f"Fish Audio model '{self._settings.model}' requires API credit (402). "
                "Set FISH_AUDIO_MODEL to a free model or add credit to the account."
            )
        if self._is_voice_not_found(status, detail):
            return (
                f"Fish Audio voice '{voice_id}' was not found ({status}). "
                "Reconfigure voice_id with a reference_id that exists and is visible to this account."
            )
        if status in (400, 422):
            return f"Fish Audio rejected the request ({status}): {detail}"
        return f"Fish Audio request failed with status {status}: {detail}"

    @staticmethod
    def _is_voice_not_found(status: int, detail: str) -> bool:
        """Detect a missing or invisible voice model.

        The API documents 404 for this case, but an unknown ``reference_id`` was
        measured answering ``400 Reference not found`` (2026-10-07). Both are
        mapped to the actionable message; other 400s keep the generic one.
        """
        if status == 404:
            return True
        lowered = detail.lower()
        return status == 400 and "reference" in lowered and "not found" in lowered

    def _extract_detail(self, body: str) -> str:
        """Pull the API's own message out of an error body, bounded and redacted.

        The body is remote text that ends up in a log line and a Discord reply,
        so it is truncated and scrubbed of the credential before being relayed.
        """
        detail = body
        try:
            parsed = json.loads(body)
        except (TypeError, ValueError):
            parsed = None
        if isinstance(parsed, dict):
            message = parsed.get("message")
            if isinstance(message, str) and message:
                detail = message
        detail = self._redact_api_key(detail).strip()
        if len(detail) > _FISH_AUDIO_ERROR_DETAIL_LIMIT:
            return detail[:_FISH_AUDIO_ERROR_DETAIL_LIMIT] + "..."
        return detail or "no detail reported"

    def _redact_api_key(self, text: str) -> str:
        """Remove the credential from any text relayed from outside this process.

        Defensive: the API is not expected to echo the key, but a relayed error
        body and a transport exception string are the places where text this
        engine did not author reaches a log, a Redis queue item and an OTel
        span, so it does not depend on the provider's discretion.

        This reduces one specific exposure; it is not a general guarantee. A
        case-shifted, truncated or re-encoded echo would defeat a string match,
        and chasing those would be theatre. What actually protects the
        credential is that it lives only in a request header, never in a body,
        a URL or a log, and that redirects are not followed.

        No length floor: a short key is still a disclosed credential, and a
        message mangled into asterisks is strictly preferable to one that leaks.
        Only the empty key is guarded, because ``str.replace("")`` would splice
        the marker between every character.
        """
        key = self._settings.api_key.strip()
        if key and key in text:
            return text.replace(key, "***")
        return text

    @staticmethod
    def _map_rate(rate: int) -> float:
        """Map the shared rate scale onto Fish Audio's prosody speed multiplier.

        ``rate`` is 50-300 around a 180 baseline; ``prosody.speed`` is 0.5-2.0
        around 1.0. Mirrors the mapping precedent in ``EdgeTTSEngine._map_rate``.
        """
        baseline = 180
        speed = rate / baseline
        return round(max(0.5, min(2.0, speed)), 3)


class RoutedTTSEngine(ITTSEngine):
    """Route audio generation to the engine requested by the current config."""

    def __init__(self, fish_audio: FishAudioSettings | None = None):
        """Initialize the router.

        Args:
            fish_audio: Provider settings for the Fish Audio engine. Omitted
                means the engine is unavailable and selecting it fails with a
                configuration error rather than a network call.
        """
        self._engines: dict[str, ITTSEngine] = {}
        self._fish_audio = fish_audio

    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        engine_key = config.engine.lower()
        engine = self._engines.get(engine_key)
        if engine is None:
            engine = TTSEngineFactory.create(config, fish_audio=self._fish_audio)
            self._engines[engine_key] = engine
        return await engine.generate_audio(text, config)


class TTSEngineFactory:
    """Factory for creating TTS engines.

    Follows Open/Closed Principle: easy to extend with new engines.
    """

    @staticmethod
    def create(config: TTSConfig, *, fish_audio: FishAudioSettings | None = None) -> ITTSEngine:
        """Create TTS engine based on configuration.

        Args:
            config: TTS configuration
            fish_audio: Provider settings required by the ``fish-audio`` engine.
                Passed in by the composition root rather than read from the
                environment here, so this factory stays free of I/O.

        Returns:
            ITTSEngine implementation

        Raises:
            ValueError: If engine type is unknown
            FishAudioError: If ``fish-audio`` is selected without a credential
        """
        if config.engine == "gtts":
            return GTTSEngine()
        if config.engine == "pyttsx3":
            return Pyttsx3Engine()
        if config.engine == "edge-tts":
            return EdgeTTSEngine()
        if config.engine == "fish-audio":
            if fish_audio is None:
                raise FishAudioError("Fish Audio API key is not configured; set FISH_AUDIO")
            return FishAudioEngine(fish_audio)
        raise ValueError(f"Unknown TTS engine: {config.engine}")
