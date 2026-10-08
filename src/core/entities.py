"""Domain entities - pure business objects without external dependencies."""

import re
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Optional
from uuid import uuid4


@dataclass
class TTSRequest:
    """Represents a text-to-speech request."""

    text: str
    channel_id: int | None = None
    guild_id: int | None = None
    member_id: int | None = None
    config_override: Optional["TTSConfig"] = None


SUPPORTED_TTS_ENGINES: tuple[str, ...] = ("gtts", "pyttsx3", "edge-tts", "fish-audio")
"""Engine identifiers accepted by configuration and runtime validation.

Single source of truth: the bot's startup validation and the ``/config`` use
case both read this, so the two cannot drift apart.
"""

DEFAULT_FISH_AUDIO_MODEL = "s2.1-pro-free"
"""Model sent as the Fish Audio ``model`` request header when none is configured.

Lives here rather than in the engine so settings can default it without the
configuration layer depending on infrastructure. The free model costs neither
API credit nor platform quota but is announced only through 2026-11-30; omitting
the header entirely falls back to the paid default, which answers 402.
"""

_FISH_AUDIO_REFERENCE_ID_PATTERN = re.compile(r"[0-9a-fA-F]{32}")


def normalize_fish_audio_reference_id(value: str) -> str | None:
    """Return the canonical Fish Audio ``reference_id``, or None if malformed.

    Returning the normalized value instead of a boolean is deliberate: a caller
    that validates gets back exactly the string it should persist and transmit,
    so validation and storage cannot disagree. Validating a stripped value and
    then storing the raw one sent the surrounding whitespace to the provider and
    produced the very failure the check exists to prevent.

    Only the shape is checked. Verifying that the voice exists would add a
    network round trip to configuration and would still race against the voice
    being deleted afterwards, so a well-formed but missing voice is reported at
    synthesis time instead.

    ``fullmatch`` is deliberate: an anchored ``$`` would accept a trailing
    newline, and a pasted identifier often carries one.
    """
    candidate = value.strip()
    return candidate if _FISH_AUDIO_REFERENCE_ID_PATTERN.fullmatch(candidate) else None


@dataclass(frozen=True)
class TTSConfig:
    """TTS engine configuration.

    Frozen: this value object is shared across every layer and is handed out by
    config repositories. Build a modified copy with ``dataclasses.replace``
    rather than mutating an instance a repository may still hold.
    """

    engine: str = "gtts"  # one of SUPPORTED_TTS_ENGINES
    language: str = "pt"
    voice_id: str = "roa/pt-br"
    rate: int = 180
    output_device: str | None = None


@dataclass
class AudioFile:
    """Represents an audio file path."""

    path: str


class AudioQueueItemStatus(StrEnum):
    """Status of an audio queue item."""

    PENDING = "pending"  # Waiting for processing
    PROCESSING = "processing"  # Being processed
    COMPLETED = "completed"  # Completed successfully
    FAILED = "failed"  # Failed


@dataclass
class AudioQueueItem:
    """Represents an item in the audio queue.

    Tracks a TTS request through the processing pipeline,
    supporting queue-based execution for multiple users.
    """

    request: TTSRequest
    item_id: str = field(default_factory=lambda: f"audio_{uuid4().hex}")
    status: AudioQueueItemStatus = AudioQueueItemStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None
    error_message: str | None = None
    trace_context: dict[str, str] | None = None
    position_in_queue: int = 0  # Queue position (0 = next to process)

    def mark_processing(self):
        """Mark item as currently being processed."""
        self.status = AudioQueueItemStatus.PROCESSING
        self.started_at = time.time()

    def mark_completed(self):
        """Mark item as successfully completed."""
        self.status = AudioQueueItemStatus.COMPLETED
        self.completed_at = time.time()

    def mark_failed(self, error: str):
        """Mark item as failed with error message.

        Args:
            error: Error description
        """
        self.status = AudioQueueItemStatus.FAILED
        self.error_message = error
        self.completed_at = time.time()

    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds if completed."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return 0.0

    @property
    def wait_time_seconds(self) -> float:
        """Get time waited in queue before processing."""
        if self.started_at:
            return self.started_at - self.created_at
        return time.time() - self.created_at
